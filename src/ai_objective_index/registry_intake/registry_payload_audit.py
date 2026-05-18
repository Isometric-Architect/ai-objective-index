from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_payload_guard import detect_payload_mode, is_fixture_payload, summarize_payload_path


DEFAULT_OUTPUT = Path("data/registry/registry_payload_audit_v0_1.json")


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


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def run_registry_payload_audit(registry_dir: str | Path = "data/registry") -> dict[str, Any]:
    root = _resolve(registry_dir)
    raw_path = root / "mcp_registry_raw_v0_1.json"
    root_raw_path = _repo_root() / "mcp_registry_raw_v0_1.json"
    raw_summary = summarize_payload_path(raw_path)
    raw_mode = detect_payload_mode(raw_path)
    root_raw_mode = detect_payload_mode(root_raw_path)
    objects = _read_jsonl(root / "mcp_registry_objects_v0_1.jsonl")
    traces = _read_jsonl(root / "mcp_registry_source_traces_v0_1.jsonl")
    candidates = _read_jsonl(root / "mcp_registry_beta_candidates_v0_1.jsonl")
    public_beta = _read_json(root / "mcp_registry_public_beta_mcp_dataset_v0_1.json")

    fixture_object_count = sum(1 for item in objects if is_fixture_payload(item))
    fixture_candidate_count = sum(1 for item in candidates if is_fixture_payload(item))
    public_beta_mcp_count = int(public_beta.get("beta_candidate_count", len(candidates) if candidates else 0) or 0)
    fixture_leak = (
        raw_mode in {"manual_raw", "live_raw"} and fixture_object_count > 0
    ) or fixture_candidate_count > 0 or (raw_mode == "fixture" and public_beta_mcp_count > 0)
    warnings: list[str] = []
    if raw_mode == "missing":
        warnings.append("Manual raw registry payload is missing.")
    if raw_mode == "fixture":
        warnings.append("Current raw registry payload is fixture data; public_beta_mcp should remain empty.")
    if raw_mode == "fixture" and root_raw_mode in {"manual_raw", "live_raw"}:
        warnings.append("Root-level manual raw payload is available; run real_payload_activation --use-existing-raw.")
    if fixture_leak:
        warnings.append("Fixture leak detected in registry objects or public_beta_mcp candidates.")
    if raw_mode in {"manual_raw", "live_raw"} and public_beta_mcp_count == 0:
        warnings.append("Real/manual raw is available but no public_beta_mcp candidates are currently built.")

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "raw_payload_mode": raw_mode,
        "root_raw_payload_mode": root_raw_mode,
        "raw_server_count": raw_summary.get("record_count", 0),
        "object_count": len(objects),
        "trace_count": len(traces),
        "beta_candidate_count": len(candidates),
        "public_beta_mcp_count": public_beta_mcp_count,
        "fixture_leak_detected": fixture_leak,
        "real_payload_available": raw_mode in {"manual_raw", "live_raw"},
        "root_manual_raw_available": root_raw_mode in {"manual_raw", "live_raw"},
        "default_scope_sample_unchanged": True,
        "warnings": warnings,
        "recommended_next_action": (
            "Run registry_reprocess_all."
            if raw_mode in {"manual_raw", "live_raw"} and not fixture_leak
            else "Download GET /v0.1/servers JSON and save as data/registry/mcp_registry_raw_v0_1.json."
        ),
    }


def save_registry_payload_audit(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT,
) -> Path:
    payload = results or run_registry_payload_audit()
    destination = _resolve(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    payload = run_registry_payload_audit()
    path = save_registry_payload_audit(payload)
    print(
        "registry_payload_audit: "
        f"raw_mode={payload['raw_payload_mode']} "
        f"raw_servers={payload['raw_server_count']} "
        f"objects={payload['object_count']} "
        f"traces={payload['trace_count']} "
        f"public_beta_mcp={payload['public_beta_mcp_count']} "
        f"fixture_leak={payload['fixture_leak_detected']}"
    )
    print(f"saved={path}")


if __name__ == "__main__":
    main()
