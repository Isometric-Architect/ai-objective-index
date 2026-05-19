from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.report_metrics import compute_missing_field_stats, compute_source_trace_coverage

from .mcp_registry_loader import load_registry_objects, load_registry_source_traces
from .registry_beta_dataset_builder import build_registry_beta_dataset


DEFAULT_OUTPUT = Path("data/registry/mcp_registry_quality_audit_v0_1.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def run_registry_quality_audit() -> dict[str, Any]:
    objects = load_registry_objects()
    traces = load_registry_source_traces()
    gate_path = _resolve("data/registry/mcp_registry_beta_candidate_gate_results_v0_1.json")
    gate = _read_json(gate_path)
    if not gate:
        gate = build_registry_beta_dataset()

    docs = [item.docs if isinstance(item.docs, dict) else {} for item in objects]
    warning_counts = Counter(
        warning
        for result in gate.get("object_results", [])
        for warning in result.get("warnings", [])
    )
    hold_counts = Counter(
        hold
        for result in gate.get("object_results", [])
        for hold in result.get("holds", [])
    )
    blocked_counts = Counter(
        block
        for result in gate.get("object_results", [])
        for block in result.get("blocks", [])
    )
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "object_count": len(objects),
        "trace_count": len(traces),
        "beta_candidate_count": int(gate.get("beta_candidate_count", 0)),
        "objects_with_description": sum(1 for item in objects if item.summary),
        "objects_with_repository": sum(1 for item, doc in zip(objects, docs) if doc.get("repository_url") or doc.get("github_url")),
        "objects_with_packages": sum(1 for item in objects if getattr(item, "package_metadata", None)),
        "objects_with_remote_metadata": sum(1 for item in objects if getattr(item, "remote_metadata", None)),
        "objects_with_install_metadata": sum(1 for item in objects if getattr(item, "integration_methods", None)),
        "source_trace_coverage": compute_source_trace_coverage(objects, traces),
        "missing_field_stats": compute_missing_field_stats(objects),
        "warning_counts": dict(warning_counts),
        "blocked_counts": dict(blocked_counts),
        "hold_counts": dict(hold_counts),
        "quality_notes": [
            "Registry metadata is useful for discovery but is not supplier verification.",
            "Missing pricing and policy fields are expected for many MCP registry records.",
            "Candidate status is not a security certification, quality guarantee, or action permission.",
        ],
    }
    return payload


def save_registry_quality_audit(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT,
) -> Path:
    payload = results or run_registry_quality_audit()
    destination = _resolve(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    payload = run_registry_quality_audit()
    path = save_registry_quality_audit(payload)
    print(
        "registry_quality_audit: "
        f"objects={payload['object_count']} "
        f"traces={payload['trace_count']} "
        f"beta_candidates={payload['beta_candidate_count']} "
        f"coverage={payload['source_trace_coverage']}"
    )
    print(f"saved={path}")


if __name__ == "__main__":
    main()
