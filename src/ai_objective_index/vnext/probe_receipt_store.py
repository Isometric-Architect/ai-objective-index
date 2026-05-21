from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .execution_receipt_validation import redact_token_like_text
from .probe_card import CapabilityProbeMemory, ProbeReceipt, ProbeResult, utc_now


DEFAULT_PROBE_RECEIPT_STORE_PATH = Path("data") / "vnext" / "probe_receipts.jsonl"
DEFAULT_PROBE_RECEIPT_INDEX_PATH = Path("data") / "vnext" / "probe_receipt_index.json"
SAMPLE_PROBE_RECEIPT_STORE_PATH = Path("data") / "vnext" / "sample_probe_receipts.jsonl"
SAMPLE_PROBE_RECEIPT_INDEX_PATH = Path("data") / "vnext" / "sample_probe_receipt_index.json"


def _repo_relative(path: Path) -> Path:
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _sanitize_strings(value: Any) -> tuple[Any, bool]:
    if isinstance(value, str):
        return redact_token_like_text(value)
    if isinstance(value, list):
        changed = False
        items = []
        for item in value:
            safe, did_change = _sanitize_strings(item)
            changed = changed or did_change
            items.append(safe)
        return items, changed
    if isinstance(value, dict):
        changed = False
        payload = {}
        for key, item in value.items():
            safe, did_change = _sanitize_strings(item)
            changed = changed or did_change
            payload[key] = safe
        return payload, changed
    return value, False


def sanitize_probe_receipt(receipt: ProbeReceipt) -> tuple[ProbeReceipt, bool]:
    payload = receipt.model_dump(mode="json", by_alias=True)
    safe_payload, token_redacted = _sanitize_strings(payload)
    return ProbeReceipt.model_validate(safe_payload), token_redacted


def _memory_status(results: list[ProbeResult]) -> str:
    if not results:
        return "NO_PROBES"
    has_block = any(result.result.startswith("BLOCK") for result in results)
    has_hold = any(result.result.startswith("HOLD") for result in results)
    has_pass = any(result.result == "PASS_LOCAL" for result in results)
    if has_block:
        return "BLOCK_SIGNALS"
    if has_hold and has_pass:
        return "MIXED_SIGNALS"
    if has_hold:
        return "HOLD_SIGNALS"
    return "LOCAL_PROBES_AVAILABLE"


class ProbeReceiptStore:
    def __init__(
        self,
        receipt_path: str | Path = DEFAULT_PROBE_RECEIPT_STORE_PATH,
        index_path: str | Path = DEFAULT_PROBE_RECEIPT_INDEX_PATH,
    ) -> None:
        self.receipt_path = _repo_relative(Path(receipt_path))
        self.index_path = _repo_relative(Path(index_path))

    def _ensure_parent(self) -> None:
        self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_records(self) -> list[dict[str, Any]]:
        if not self.receipt_path.exists():
            return []
        records = []
        for line in self.receipt_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        return records

    def _write_index(self, records: list[dict[str, Any]]) -> None:
        receipts = []
        for record in records:
            receipt = record.get("receipt", record)
            receipts.append(
                {
                    "receipt_id": receipt.get("receipt_id"),
                    "plan_id": receipt.get("plan_id"),
                    "result_count": len(receipt.get("probe_results", [])),
                    "route_effect": receipt.get("route_effect"),
                    "stored_at": record.get("stored_at"),
                }
            )
        index = {
            "schema": "AOI_ProbeReceiptIndex/v0.1",
            "receipt_count": len(records),
            "receipts": receipts,
            "token_printed": False,
        }
        self.index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def append_probe_receipt(self, receipt: ProbeReceipt) -> dict[str, Any]:
        self._ensure_parent()
        safe_receipt, token_redacted = sanitize_probe_receipt(receipt)
        record = {
            "schema": "AOI_StoredProbeReceipt/v0.1",
            "receipt": safe_receipt.model_dump(mode="json", by_alias=True),
            "stored_at": utc_now(),
            "token_redacted": token_redacted,
            "token_printed": False,
        }
        with self.receipt_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        records = self._load_records()
        self._write_index(records)
        return record

    def get_probe_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        for record in self._load_records():
            receipt = record.get("receipt", record)
            if receipt.get("receipt_id") == receipt_id:
                return record
        return None

    def list_probe_receipts(
        self,
        capability_id: str | None = None,
        plan_id: str | None = None,
        result: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        records = self._load_records()
        filtered = []
        for record in records:
            receipt = record.get("receipt", record)
            if plan_id is not None and receipt.get("plan_id") != plan_id:
                continue
            results = receipt.get("probe_results", [])
            if capability_id is not None and not any(item.get("capability_id") == capability_id for item in results):
                continue
            if result is not None and not any(item.get("result") == result for item in results):
                continue
            filtered.append(record)
        return filtered[-max(1, limit) :]

    def build_capability_probe_memory(self, capability_id: str) -> CapabilityProbeMemory:
        receipts = self.list_probe_receipts(capability_id=capability_id, limit=1000)
        results: list[ProbeResult] = []
        for record in receipts:
            receipt = record.get("receipt", record)
            for item in receipt.get("probe_results", []):
                if item.get("capability_id") == capability_id:
                    results.append(ProbeResult.model_validate(item))
        if not results:
            return CapabilityProbeMemory(capability_id=capability_id)
        counts = Counter(result.result for result in results)
        holds = sorted({finding for result in results if result.result.startswith("HOLD") for finding in result.findings + result.warnings})
        blocks = sorted({finding for result in results if result.result.startswith("BLOCK") for finding in result.findings + result.errors})
        findings = Counter(finding for result in results for finding in result.findings)
        negative_status = "passed" if any(result.probe_id.startswith("probe-") and result.result.startswith("BLOCK") for result in results) else "not_checked"
        return CapabilityProbeMemory(
            capability_id=capability_id,
            probe_count=len(results),
            latest_probe_result=results[-1].result,
            hold_reasons=holds[:10],
            block_reasons=blocks[:10],
            recurring_findings=[item for item, _ in findings.most_common(10)],
            negative_control_status=negative_status,
            can_influence_route=True,
            memory_status=_memory_status(results),  # type: ignore[arg-type]
        )
