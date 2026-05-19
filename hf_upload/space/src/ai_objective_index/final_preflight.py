from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .realdata_claim_audit import run_realdata_claim_audit, save_realdata_claim_audit
from .release_candidate_matrix import build_release_candidate_matrix, save_release_candidate_matrix
from .release_readiness import run_release_readiness, save_release_readiness
from .smoke_all import run_smoke_all


DEFAULT_OUTPUT_PATH = Path("data/generated/final_preflight_result_v0_2.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: str) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        value = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _read_text(path: str) -> str:
    full = _repo_root() / path
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


def _exists(path: str) -> bool:
    return (_repo_root() / path).exists()


def _token(condition: bool, block: bool = False) -> str:
    if block:
        return "BLOCK"
    return "PASS" if condition else "HOLD"


def _beta_readiness_token() -> str:
    text = _read_text("data/generated/beta_readiness_report_v0_2.md")
    if "Overall readiness token: `PASS`" in text or "beta_readiness=PASS" in text:
        return "PASS"
    if "Overall readiness token: `BLOCK`" in text:
        return "BLOCK"
    return "HOLD"


def _manifest_forbidden_actions_exposed() -> bool:
    manifest = _read_json("data/generated_mcp_tools_manifest.json")
    tool_names = {tool.get("name") for tool in manifest.get("tools", []) if isinstance(tool, dict)}
    forbidden = set(manifest.get("forbidden_actions", []))
    return bool(tool_names & forbidden)


def run_final_preflight() -> dict[str, Any]:
    required_artifacts = [
        "data/generated/datascope_qa_results_v0_2.json",
        "data/generated/beta_readiness_report_v0_2.md",
        "data/registry/registry_payload_audit_v0_1.json",
        "data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json",
        "data/registry/mcp_registry_beta_candidates_v0_1.jsonl",
        "data/registry/mcp_registry_beta_report_v0_1.md",
        "api/openapi.json",
        "data/generated_mcp_tools_manifest.json",
    ]
    missing_artifacts = [path for path in required_artifacts if not _exists(path)]
    registry_audit = _read_json("data/registry/registry_payload_audit_v0_1.json")
    registry_dataset = _read_json("data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json")
    datascope = _read_json("data/generated/datascope_qa_results_v0_2.json")
    scopes = datascope.get("scopes", {}) if isinstance(datascope.get("scopes"), dict) else {}

    public_beta_mcp_count = int(
        registry_audit.get("public_beta_mcp_count")
        or registry_dataset.get("beta_candidate_count")
        or scopes.get("public_beta_mcp", {}).get("object_count", 0)
        or 0
    )
    mcp_registry_count = int(
        registry_audit.get("object_count")
        or registry_dataset.get("object_count")
        or scopes.get("mcp_registry", {}).get("object_count", 0)
        or 0
    )
    trace_count = int(registry_audit.get("trace_count") or registry_dataset.get("trace_count") or 0)
    raw_mode = str(registry_audit.get("raw_payload_mode", "missing"))

    claim_audit = run_realdata_claim_audit()
    claim_audit_path = save_realdata_claim_audit(claim_audit)
    matrix = build_release_candidate_matrix()
    matrix_path = save_release_candidate_matrix(matrix)
    smoke = run_smoke_all()
    release_readiness = run_release_readiness()
    release_readiness_path = save_release_readiness(release_readiness)
    beta_token = _beta_readiness_token()

    checks = {
        "required_artifacts": {
            "token": _token(not missing_artifacts),
            "missing": missing_artifacts,
        },
        "real_registry_data": {
            "token": _token(
                mcp_registry_count > 0
                and public_beta_mcp_count > 0
                and raw_mode in {"manual_raw", "live_raw"}
                and registry_audit.get("fixture_leak_detected") is False
                and registry_audit.get("real_payload_available") is True
            ),
            "raw_payload_mode": raw_mode,
            "mcp_registry_object_count": mcp_registry_count,
            "public_beta_mcp_count": public_beta_mcp_count,
            "fixture_leak_detected": registry_audit.get("fixture_leak_detected"),
            "real_payload_available": registry_audit.get("real_payload_available"),
        },
        "safety": {
            "token": _token(
                not _manifest_forbidden_actions_exposed()
                and registry_audit.get("live_network_used") is False
                and datascope.get("live_network_used") is False
            ),
            "forbidden_actions_exposed": _manifest_forbidden_actions_exposed(),
            "live_crawling_used": False,
            "scraping_used": False,
            "link_following_used": False,
            "actual_publish_performed": False,
        },
        "claim_boundary": {
            "token": claim_audit["overall_token"],
            "risky_phrase_count": claim_audit["risky_phrase_count"],
            "claim_audit_path": str(claim_audit_path),
        },
        "smoke_all": {
            "token": _token(bool(smoke.get("pass"))),
            "output_path": smoke.get("output_path"),
        },
        "release_readiness": {
            "token": release_readiness["overall_token"],
            "output_path": str(release_readiness_path),
        },
        "beta_readiness": {
            "token": beta_token,
            "output_path": "data/generated/beta_readiness_report_v0_2.md",
        },
        "release_candidate_matrix": {
            "token": matrix["overall_token"],
            "output_path": str(matrix_path),
        },
    }
    warnings: list[str] = []
    for name, check in checks.items():
        if check["token"] != "PASS":
            warnings.append(f"{name} returned {check['token']}.")
    if public_beta_mcp_count > 0:
        warnings.append("public_beta_mcp contains registry metadata candidates, not verified MCP servers.")

    if any(check["token"] == "BLOCK" for check in checks.values()):
        overall = "BLOCK"
    elif all(check["token"] == "PASS" for check in checks.values()):
        overall = "PASS"
    else:
        overall = "HOLD"

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "checks": checks,
        "counts": {
            "mcp_registry_object_count": mcp_registry_count,
            "source_trace_count": trace_count,
            "public_beta_mcp_count": public_beta_mcp_count,
        },
        "warnings": warnings,
        "recommended_next_action": "Manual public beta packaging may proceed; no publish was performed."
        if overall == "PASS"
        else "Review HOLD/BLOCK checks before manual release.",
        "actual_publish_performed": False,
        "live_network_used_in_preflight": False,
        "read_only": True,
        "not_asserted": [
            "supplier_verification",
            "security_certification",
            "quality_guarantee",
            "action_permission",
            "purchasing_advice",
        ],
    }


def save_final_preflight(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or run_final_preflight()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_final_preflight()
    path = save_final_preflight(results)
    print(f"Saved final preflight result: {path}")
    print(
        "final_preflight: "
        f"{results['overall_token']} "
        f"public_beta_mcp={results['counts']['public_beta_mcp_count']} "
        "actual_publish_performed=False "
        "live_network_used_in_preflight=False"
    )


if __name__ == "__main__":
    main()
