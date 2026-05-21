from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OUTPUT_PATH = Path("public_launch") / "wave8" / "VNEXT_SURFACE_SYNC_AUDIT.json"

REST_ENDPOINTS = [
    "/v1/objectives/route",
    "/v1/objectives/trust-report",
    "/v1/capabilities/{capability_id}/trust",
    "/v1/objectives/router/status",
    "/v1/execution-receipts",
    "/v1/execution-receipts/{receipt_id}",
    "/v1/capabilities/{capability_id}/execution-receipts",
    "/v1/capabilities/{capability_id}/receipt-memory",
    "/v1/objectives/{objective_id}/receipt-summary",
    "/v1/objectives/route-with-receipts",
    "/v1/execution-receipts/status",
    "/v1/probes/plan",
    "/v1/probes/run-local",
    "/v1/probes/{receipt_id}",
    "/v1/capabilities/{capability_id}/probe-memory",
    "/v1/objectives/route-with-probes",
    "/v1/probes/status",
]

MCP_TOOLS = [
    "route_objective",
    "get_capability_trust",
    "explain_route_decision",
    "submit_execution_receipt",
    "get_execution_receipt",
    "list_capability_receipts",
    "get_capability_receipt_memory",
    "route_objective_with_receipts",
    "plan_probe_before_use",
    "run_local_probe_plan",
    "get_probe_receipt",
    "get_capability_probe_memory",
    "route_objective_with_probes",
]

OVERCLAIMS = [
    "external security gateway",
    "security gateway",
    "security scanner",
    "verified capability",
    "safe tool",
    "security certified",
    "quality guaranteed",
    "production ready",
    "production-ready",
    "action authorization",
]

ALLOWED_CONTEXT = [
    "not ",
    "no ",
    "cannot ",
    "does not ",
    "do not ",
    "must not ",
    "not already",
    "not a security gateway",
    "not verification",
    "not implemented",
    "not security certified",
    "not a quality guarantee",
    "not external",
    "no action authorization",
    "without external",
    "claim boundary",
    "claim ",
    "claiming ",
    "forbidden",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read(path: str | Path) -> str:
    full = _repo_root() / path
    return full.read_text(encoding="utf-8", errors="ignore") if full.exists() else ""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _has_unallowed_occurrence(text: str, phrase: str) -> bool:
    lowered = text.lower()
    start = 0
    while True:
        index = lowered.find(phrase, start)
        if index < 0:
            return False
        context = lowered[max(0, index - 220) : index + len(phrase) + 120]
        if not any(marker in context for marker in ALLOWED_CONTEXT):
            return True
        start = index + len(phrase)


def audit_surface_text(readme_text: str, docs_text: str = "") -> dict[str, Any]:
    combined = (readme_text + "\n" + docs_text).lower()
    required_readme = {
        "objective_to_capability_router": (
            "objective-to-capability" in combined
            or "capability trust router" in combined
            or "ai agent capability trust router" in combined
        ),
        "read_only": "read-only" in combined,
        "source_traced": "source-traced" in combined or "source trace" in combined,
        "not_verified": "not verified" in combined,
        "not_security_certified": "not security certified" in combined,
        "not_quality_guarantee": "not a quality guarantee" in combined or "not quality guarantee" in combined,
    }
    overclaim_findings = [phrase for phrase in OVERCLAIMS if _has_unallowed_occurrence(combined, phrase)]
    return {"required_readme": required_readme, "overclaim_findings": overclaim_findings}


def run_vnext_surface_sync_audit(write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    readme = _read("README.md")
    docs_paths = [
        root / "docs" / "api_reference.md",
        root / "docs" / "mcp_usage.md",
        root / "docs" / "vnext" / "aoi_vnext_strategy.md",
        root / "docs" / "vnext" / "do_not_overclaim_vnext.md",
        root / "docs" / "launch_notes.md",
    ]
    docs_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in docs_paths if path.exists())
    text_audit = audit_surface_text(readme, docs_text)
    docs_combined = (readme + "\n" + docs_text).lower()
    api_openapi = root / "api" / "openapi.json"
    vnext_openapi = root / "api" / "vnext" / "objective_router_openapi.json"
    manifest_path = root / "data" / "generated_mcp_tools_manifest.json"
    manifest_text = manifest_path.read_text(encoding="utf-8", errors="ignore") if manifest_path.exists() else ""
    manifest_payload: dict[str, Any] = {}
    if manifest_text:
        try:
            manifest_payload = json.loads(manifest_text)
        except json.JSONDecodeError:
            manifest_payload = {}
    manifest_tools = {tool.get("name") for tool in manifest_payload.get("tools", []) if isinstance(tool, dict)}
    checks = {
        **text_audit["required_readme"],
        "openapi_exists": api_openapi.exists(),
        "vnext_openapi_exists": vnext_openapi.exists(),
        "mcp_manifest_exists": manifest_path.exists(),
        "rest_endpoints_documented": all(endpoint.lower() in docs_combined for endpoint in REST_ENDPOINTS),
        "mcp_tools_documented": all(tool in docs_combined or tool in manifest_tools for tool in MCP_TOOLS),
        "github_release_public_beta_not_stable": "public beta" in docs_combined and "stable production" not in docs_combined,
    }
    missing_surface = [key for key, ok in checks.items() if not ok]
    if text_audit["overclaim_findings"]:
        decision = "BLOCK_OVERCLAIM"
    elif any(key in missing_surface for key in ["openapi_exists", "mcp_manifest_exists", "rest_endpoints_documented", "mcp_tools_documented"]):
        decision = "BLOCK_MISSING_SURFACE"
    elif missing_surface:
        decision = "HOLD_DOCS_INCOMPLETE"
    else:
        decision = "PASS"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "overall_token": "PASS" if decision == "PASS" else ("BLOCK" if decision.startswith("BLOCK") else "HOLD"),
        "checks": checks,
        "missing_surface": missing_surface,
        "overclaim_findings": text_audit["overclaim_findings"],
        "rest_endpoints_required": REST_ENDPOINTS,
        "mcp_tools_required": MCP_TOOLS,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_vnext_surface_sync_audit()
    print(f"vnext_surface_sync_audit: {result['decision']} missing={len(result['missing_surface'])}")


if __name__ == "__main__":
    main()
