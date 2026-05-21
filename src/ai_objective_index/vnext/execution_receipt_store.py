from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .execution_receipt_loop import (
    ExecutionReceiptSubmission,
    ExecutionReceiptValidationResult,
    StoredExecutionReceipt,
)
from .execution_receipt_summary import build_capability_receipt_memory, build_objective_receipt_summary
from .execution_receipt_validation import redact_token_like_text


DEFAULT_RECEIPT_STORE_PATH = Path("data") / "vnext" / "execution_receipts.jsonl"
DEFAULT_RECEIPT_INDEX_PATH = Path("data") / "vnext" / "execution_receipt_index.json"
SAMPLE_RECEIPT_STORE_PATH = Path("data") / "vnext" / "sample_execution_receipts.jsonl"
SAMPLE_RECEIPT_INDEX_PATH = Path("data") / "vnext" / "sample_execution_receipt_index.json"


def _repo_relative(path: Path) -> Path:
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _sanitize_string(value: str) -> tuple[str, bool]:
    return redact_token_like_text(value)


def sanitize_receipt(receipt: ExecutionReceiptSubmission) -> tuple[ExecutionReceiptSubmission, bool]:
    payload = receipt.model_dump(mode="json", by_alias=True)
    changed = False
    for key in ["outcome_summary", "task_context", "capability_name", "route_decision_before", "route_decision_after"]:
        if isinstance(payload.get(key), str):
            payload[key], did_change = _sanitize_string(payload[key])
            changed = changed or did_change
    for key in ["constraints_checked", "observed_outputs", "residual_notes", "missing_fields_found"]:
        if isinstance(payload.get(key), list):
            items = []
            for item in payload[key]:
                text, did_change = _sanitize_string(str(item))
                changed = changed or did_change
                items.append(text)
            payload[key] = items
    return ExecutionReceiptSubmission.model_validate(payload), changed


class ExecutionReceiptStore:
    def __init__(
        self,
        receipt_path: str | Path = DEFAULT_RECEIPT_STORE_PATH,
        index_path: str | Path = DEFAULT_RECEIPT_INDEX_PATH,
    ) -> None:
        self.receipt_path = _repo_relative(Path(receipt_path))
        self.index_path = _repo_relative(Path(index_path))

    def _ensure_parent(self) -> None:
        self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_records(self) -> list[StoredExecutionReceipt]:
        if not self.receipt_path.exists():
            return []
        records: list[StoredExecutionReceipt] = []
        for line in self.receipt_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            records.append(StoredExecutionReceipt.model_validate(json.loads(line)))
        return records

    def _write_index(self, records: list[StoredExecutionReceipt]) -> None:
        index: dict[str, Any] = {
            "schema": "AOI_ExecutionReceiptIndex/v0.1",
            "receipt_count": len(records),
            "receipts": [
                {
                    "receipt_id": record.receipt.receipt_id,
                    "capability_id": record.receipt.capability_id,
                    "objective_id": record.receipt.objective_id,
                    "outcome": record.receipt.outcome,
                    "validation_decision": record.validation.decision,
                    "stored_at": record.stored_at,
                }
                for record in records
            ],
            "token_printed": False,
        }
        self.index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def append_receipt(
        self,
        receipt: ExecutionReceiptSubmission,
        validation_result: ExecutionReceiptValidationResult,
    ) -> StoredExecutionReceipt:
        self._ensure_parent()
        sanitized, token_redacted = sanitize_receipt(receipt)
        record = StoredExecutionReceipt(
            receipt=sanitized,
            validation=validation_result,
            token_redacted=token_redacted,
        )
        with self.receipt_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.model_dump(mode="json", by_alias=True), ensure_ascii=False) + "\n")
        records = self._load_records()
        self._write_index(records)
        return record

    def get_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        for record in self._load_records():
            if record.receipt.receipt_id == receipt_id:
                return record.model_dump(mode="json", by_alias=True)
        return None

    def list_receipts(
        self,
        capability_id: str | None = None,
        objective_id: str | None = None,
        outcome: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        records = self._load_records()
        if capability_id is not None:
            records = [record for record in records if record.receipt.capability_id == capability_id]
        if objective_id is not None:
            records = [record for record in records if record.receipt.objective_id == objective_id]
        if outcome is not None:
            records = [record for record in records if record.receipt.outcome == outcome]
        return [record.model_dump(mode="json", by_alias=True) for record in records[-max(1, limit) :]]

    def summarize_by_capability(self, capability_id: str) -> dict[str, Any]:
        return self.build_memory(capability_id).model_dump(mode="json", by_alias=True)

    def summarize_by_objective(self, objective_id: str) -> dict[str, Any]:
        return build_objective_receipt_summary(objective_id, self._load_records()).model_dump(mode="json", by_alias=True)

    def build_memory(self, capability_id: str):
        return build_capability_receipt_memory(capability_id, self._load_records())
