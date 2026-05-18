from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.beta_readiness import write_beta_readiness_report
from ai_objective_index.datascope_qa import run_datascope_qa, save_datascope_qa_results
from ai_objective_index.mcp_manifest import save_mcp_tool_manifest
from ai_objective_index.openapi_export import export_openapi
from ai_objective_index.release_readiness import run_release_readiness, save_release_readiness

from .mcp_registry_eval import run_mcp_registry_eval, save_mcp_registry_eval
from .mcp_registry_export import export_mcp_registry_intake
from .mcp_registry_report_generator import write_mcp_registry_report
from .real_payload_guard import detect_payload_mode
from .registry_beta_dataset_builder import build_registry_beta_dataset
from .registry_beta_report_generator import write_registry_beta_report
from .registry_payload_audit import run_registry_payload_audit, save_registry_payload_audit
from .registry_quality_audit import run_registry_quality_audit, save_registry_quality_audit


DEFAULT_OUTPUT = Path("data/registry/registry_reprocess_all_result_v0_1.json")
FALLBACK_MESSAGE = "Download GET /v0.1/servers JSON and save as data/registry/mcp_registry_raw_v0_1.json."


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def run_registry_reprocess_all(
    raw_path: str | Path = "data/registry/mcp_registry_raw_v0_1.json",
    output_path: str | Path = DEFAULT_OUTPUT,
    max_servers: int = 50,
) -> dict[str, Any]:
    resolved_raw = _resolve(raw_path)
    payload_mode = detect_payload_mode(resolved_raw)
    warnings: list[str] = []
    errors: list[str] = []
    generated_files: list[str] = []

    if payload_mode == "missing":
        result = {
            "generated_at": datetime.now(UTC).isoformat(),
            "read_only": True,
            "live_network_used": False,
            "payload_mode": payload_mode,
            "success": False,
            "manual_raw_needed": True,
            "warnings": [FALLBACK_MESSAGE],
            "errors": [],
            "next_action": FALLBACK_MESSAGE,
            "public_beta_mcp_count": 0,
        }
        _write_json(_resolve(output_path), result)
        return result

    if payload_mode == "unknown":
        result = {
            "generated_at": datetime.now(UTC).isoformat(),
            "read_only": True,
            "live_network_used": False,
            "payload_mode": payload_mode,
            "success": False,
            "manual_raw_needed": True,
            "warnings": ["Raw registry payload is not recognized as fixture or Official MCP Registry JSON.", FALLBACK_MESSAGE],
            "errors": [],
            "next_action": FALLBACK_MESSAGE,
            "public_beta_mcp_count": 0,
        }
        _write_json(_resolve(output_path), result)
        return result

    if payload_mode == "fixture":
        audit = run_registry_payload_audit(registry_dir=resolved_raw.parent)
        audit_path = save_registry_payload_audit(audit, path=resolved_raw.parent / "registry_payload_audit_v0_1.json")
        result = {
            "generated_at": datetime.now(UTC).isoformat(),
            "read_only": True,
            "live_network_used": False,
            "payload_mode": payload_mode,
            "success": True,
            "manual_raw_needed": True,
            "warnings": ["HOLD_FIXTURE_ONLY: fixture raw is not promoted to public_beta_mcp."],
            "errors": [],
            "beta_candidate_count": 0,
            "public_beta_mcp_count": 0,
            "generated_files": [str(audit_path)],
            "next_action": FALLBACK_MESSAGE,
        }
        _write_json(_resolve(output_path), result)
        return result

    export = export_mcp_registry_intake(
        allow_network=False,
        max_servers=max_servers,
        use_fixture=False,
        output_dir=resolved_raw.parent,
        raw_path=resolved_raw,
    )
    generated_files.extend(
        [
            "data/registry/mcp_registry_objects_v0_1.jsonl",
            "data/registry/mcp_registry_source_traces_v0_1.jsonl",
            "data/registry/mcp_registry_validation_results_v0_1.json",
            "data/registry/mcp_registry_public_beta_index_v0_1.json",
        ]
    )
    eval_result = run_mcp_registry_eval()
    eval_path = save_mcp_registry_eval(eval_result)
    registry_report = write_mcp_registry_report()
    beta = build_registry_beta_dataset()
    quality = run_registry_quality_audit()
    quality_path = save_registry_quality_audit(quality)
    beta_report = write_registry_beta_report()
    audit = run_registry_payload_audit()
    audit_path = save_registry_payload_audit(audit)
    datascope_path = save_datascope_qa_results(run_datascope_qa())
    beta_readiness_path = write_beta_readiness_report()
    release_readiness = run_release_readiness()
    release_readiness_path = save_release_readiness(release_readiness)
    openapi_path = export_openapi()
    mcp_manifest_path = save_mcp_tool_manifest()
    generated_files.extend(
        [
            str(eval_path),
            str(registry_report),
            "data/registry/mcp_registry_beta_candidates_v0_1.jsonl",
            "data/registry/mcp_registry_beta_candidate_gate_results_v0_1.json",
            str(quality_path),
            "data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json",
            str(beta_report),
            str(audit_path),
            str(datascope_path),
            str(beta_readiness_path),
            str(release_readiness_path),
            str(openapi_path),
            str(mcp_manifest_path),
        ]
    )
    warnings.extend(export.get("warnings", []))
    if audit.get("fixture_leak_detected"):
        warnings.append("Fixture leak detected by registry payload audit.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "payload_mode": payload_mode,
        "success": not errors,
        "manual_raw_needed": payload_mode == "fixture",
        "export_summary": export,
        "eval_summary": {
            "query_count": eval_result.get("query_count"),
            "result_count": eval_result.get("result_count"),
            "fixture_only": eval_result.get("fixture_only"),
        },
        "beta_candidate_count": beta.get("beta_candidate_count", 0),
        "public_beta_mcp_count": audit.get("public_beta_mcp_count", beta.get("beta_candidate_count", 0)),
        "quality_summary": {
            "source_trace_coverage": quality.get("source_trace_coverage"),
            "object_count": quality.get("object_count"),
            "trace_count": quality.get("trace_count"),
        },
        "warnings": warnings,
        "errors": errors,
        "generated_files": generated_files,
        "next_action": (
            "Review public_beta_mcp candidates."
            if payload_mode in {"manual_raw", "live_raw"} and beta.get("beta_candidate_count", 0) > 0
            else FALLBACK_MESSAGE
        ),
    }
    _write_json(_resolve(output_path), result)
    return result


def main() -> None:
    result = run_registry_reprocess_all()
    print(
        "registry_reprocess_all: "
        f"payload_mode={result['payload_mode']} "
        f"success={result['success']} "
        f"beta_candidates={result.get('beta_candidate_count', 0)} "
        f"public_beta_mcp={result.get('public_beta_mcp_count', 0)} "
        f"live_network_used={result['live_network_used']}"
    )
    if result.get("warnings"):
        print("warnings: " + " | ".join(str(item) for item in result["warnings"]))


if __name__ == "__main__":
    main()
