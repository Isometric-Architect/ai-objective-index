from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.models import ActionObject, SourceTrace

from .mcp_registry_loader import load_registry_objects, load_registry_source_traces
from .registry_candidate_gate import evaluate_registry_beta_candidate


DEFAULT_OBJECTS_PATH = Path("data/registry/mcp_registry_objects_v0_1.jsonl")
DEFAULT_TRACES_PATH = Path("data/registry/mcp_registry_source_traces_v0_1.jsonl")
DEFAULT_OUTPUT_DIR = Path("data/registry")
DEFAULT_CANDIDATES_PATH = Path("data/registry/mcp_registry_beta_candidates_v0_1.jsonl")
DEFAULT_GATE_RESULTS_PATH = Path("data/registry/mcp_registry_beta_candidate_gate_results_v0_1.json")
DEFAULT_DATASET_PATH = Path("data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _source_mode(output_dir: Path, objects: list[ActionObject]) -> str:
    summary = _read_json(output_dir / "mcp_registry_live_summary_v0_1.json")
    raw = _read_json(output_dir / "mcp_registry_raw_v0_1.json")
    public_beta = _read_json(output_dir / "mcp_registry_public_beta_index_v0_1.json")
    if any(bool(getattr(item, "fixture_only", False)) for item in objects):
        return "fixture"
    if raw.get("fixture_mode") is True or public_beta.get("fixture_mode") is True:
        return "fixture"
    if summary.get("mode") in {"manual_raw", "live_registry"} or raw.get("source") == "official_mcp_registry_api":
        return "live_or_manual_raw"
    return "live_or_manual_raw" if objects else "empty"


def _traces_by_object(traces: list[SourceTrace]) -> dict[str, list[SourceTrace]]:
    grouped: dict[str, list[SourceTrace]] = {}
    for trace in traces:
        grouped.setdefault(trace.object_id, []).append(trace)
    return grouped


def _candidate_payload(action_object: ActionObject, gate: dict[str, Any]) -> dict[str, Any]:
    payload = action_object.model_dump(mode="json")
    payload["status"] = "EXTRACTED_UNVERIFIED"
    payload["display_status"] = gate["status_to_display"]
    payload["beta_candidate"] = True
    payload["verified"] = False
    payload["action_ready"] = False
    payload["supplier_verified"] = False
    payload["not_security_certified"] = True
    payload["not_quality_guarantee"] = True
    payload["not_asserted"] = gate["not_asserted"]
    payload["candidate_warnings"] = gate["warnings"]
    return payload


def load_registry_beta_candidate_objects(
    path: str | Path = DEFAULT_CANDIDATES_PATH,
) -> list[ActionObject]:
    return [ActionObject.model_validate(row) for row in _read_jsonl(_resolve(path))]


def load_registry_beta_candidate_traces(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
) -> list[SourceTrace]:
    dataset = _read_json(_resolve(dataset_path))
    return [SourceTrace.model_validate(row) for row in dataset.get("source_traces", []) if isinstance(row, dict)]


def build_registry_beta_dataset(
    objects_path: str | Path = DEFAULT_OBJECTS_PATH,
    traces_path: str | Path = DEFAULT_TRACES_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    destination = _resolve(output_dir)
    objects = load_registry_objects(_resolve(objects_path))
    traces = load_registry_source_traces(_resolve(traces_path))
    source_mode = _source_mode(destination, objects)
    trace_map = _traces_by_object(traces)
    gate_results = [
        evaluate_registry_beta_candidate(
            action_object,
            trace_map.get(action_object.object_id, []),
            source_mode=source_mode,
        )
        for action_object in objects
    ]
    gate_by_id = {item["object_id"]: item for item in gate_results}
    candidates = [
        _candidate_payload(action_object, gate_by_id[action_object.object_id])
        for action_object in objects
        if gate_by_id[action_object.object_id]["beta_candidate"]
    ]
    candidate_ids = {item["object_id"] for item in candidates}
    candidate_traces = [
        trace.model_dump(mode="json")
        for trace in traces
        if trace.object_id in candidate_ids
    ]
    decision_counts = Counter(item["decision"] for item in gate_results)
    hold_counts = Counter(hold for item in gate_results for hold in item["holds"])
    block_counts = Counter(block for item in gate_results for block in item["blocks"])
    warnings = []
    if not candidates:
        warnings.append("No public_beta_mcp candidates passed the calibrated registry candidate gate.")
    if source_mode == "fixture":
        warnings.append("Fixture-only registry records are not promoted to public_beta_mcp.")

    gate_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "source_mode": source_mode,
        "object_count": len(objects),
        "trace_count": len(traces),
        "beta_candidate_count": len(candidates),
        "decision_counts": dict(decision_counts),
        "hold_counts": dict(hold_counts),
        "block_counts": dict(block_counts),
        "object_results": gate_results,
        "warnings": warnings,
        "not_asserted": [
            "security_certification",
            "supplier_verification",
            "quality_guarantee",
            "action_permission",
            "purchasing_advice",
        ],
    }
    dataset_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "source_mode": source_mode,
        "object_count": len(objects),
        "trace_count": len(traces),
        "beta_candidate_count": len(candidates),
        "objects": candidates,
        "source_traces": candidate_traces,
        "supplier_verified": False,
        "verified": False,
        "action_ready": False,
        "not_security_certified": True,
        "not_quality_guarantee": True,
        "not_purchasing_advice": True,
        "warnings": warnings,
    }
    _write_jsonl(destination / "mcp_registry_beta_candidates_v0_1.jsonl", candidates)
    _write_json(destination / "mcp_registry_beta_candidate_gate_results_v0_1.json", gate_payload)
    _write_json(destination / "mcp_registry_public_beta_mcp_dataset_v0_1.json", dataset_payload)
    return {
        **gate_payload,
        "candidate_path": str(destination / "mcp_registry_beta_candidates_v0_1.jsonl"),
        "gate_results_path": str(destination / "mcp_registry_beta_candidate_gate_results_v0_1.json"),
        "dataset_path": str(destination / "mcp_registry_public_beta_mcp_dataset_v0_1.json"),
    }


def main() -> None:
    result = build_registry_beta_dataset()
    print(
        "registry_beta_dataset_builder: "
        f"source_mode={result['source_mode']} "
        f"objects={result['object_count']} "
        f"traces={result['trace_count']} "
        f"beta_candidates={result['beta_candidate_count']} "
        "live_network_used=False"
    )


if __name__ == "__main__":
    main()
