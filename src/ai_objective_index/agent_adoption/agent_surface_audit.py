from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import repo_root, timestamp, write_json, write_text
from .agent_claim_boundary import scan_paths
from .capability_card import CAPABILITY_CARD_PATH, validate_capability_card
from . import read_json
from ai_objective_index.mcp_manifest import get_mcp_tool_manifest


OUTPUT_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_SURFACE_AUDIT_RESULT.json"
REST_RESULT_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_REST_SURFACE_RESULT.json"
MCP_RESULT_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_MCP_SURFACE_RESULT.json"
SUMMARY_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_ADOPTION_2_SUMMARY.md"
NEXT_ACTIONS_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_ADOPTION_2_NEXT_ACTIONS.md"

REST_PATHS = [
    "/v1/agents/capability-card",
    "/v1/agents/discover",
    "/v1/agents/preflight",
    "/v1/agents/adoption/status",
]
MCP_TOOLS = [
    "get_aoi_capability_card",
    "discover_capabilities_for_objective",
    "preflight_capability_for_use",
    "explain_aoi_agent_use",
    "list_aoi_agent_examples",
]


def _write_surface_public_outputs(result: dict[str, Any]) -> None:
    rest_result = {
        "schema": "AOI_AgentRestSurfaceResult/v0.1",
        "generated_at": result["generated_at"],
        "decision": "PASS_REST_AGENT_SURFACE_READY" if not result["missing_rest_paths"] else "HOLD_REST_AGENT_SURFACE_INCOMPLETE",
        "paths": REST_PATHS,
        "missing_paths": result["missing_rest_paths"],
        "read_only": True,
        "external_api_used": False,
        "live_mcp_call_used": False,
        "action_authorization": False,
    }
    mcp_result = {
        "schema": "AOI_AgentMcpSurfaceResult/v0.1",
        "generated_at": result["generated_at"],
        "decision": "PASS_MCP_AGENT_SURFACE_READY"
        if not result["missing_mcp_tools"] and not result["non_read_only_mcp_tools"]
        else "HOLD_MCP_AGENT_SURFACE_INCOMPLETE",
        "tools": MCP_TOOLS,
        "missing_tools": result["missing_mcp_tools"],
        "non_read_only_tools": result["non_read_only_mcp_tools"],
        "read_only": True,
        "external_api_used": False,
        "live_mcp_call_used": False,
        "action_authorization": False,
    }
    write_json(REST_RESULT_PATH, rest_result)
    write_json(MCP_RESULT_PATH, mcp_result)
    write_text(
        SUMMARY_PATH,
        f"""# AOI Agent Adoption 2 Summary

Decision: `{result['decision']}`

AOI-AGENT-ADOPTION-2 wires AOI's ordinary-agent discover/preflight pack into local read-only REST and MCP surfaces for the unpublished `0.3.0a2` package candidate.

| Surface | Status |
| --- | --- |
| REST endpoints | `{rest_result['decision']}` |
| MCP tools | `{mcp_result['decision']}` |
| OpenAPI regenerated | `{result['openapi_regenerated']}` |
| MCP manifest regenerated | `{result['mcp_manifest_regenerated']}` |
| External APIs used | `False` |
| PyPI upload performed | `False` |
| MCP Registry publish performed | `False` |

The surfaces are local and read-only. They return capability-card, discover, preflight, explanation, and example metadata with missing fields, next actions, must-not-claim boundaries, freshness/staleness signals, and ResidualOps escalation. They do not execute live tools, authorize external action, certify security, prove correctness, guarantee quality, claim product readiness, handle tokens, or expose private kernel values.
""",
    )
    write_text(
        NEXT_ACTIONS_PATH,
        """# AOI Agent Adoption 2 Next Actions

Recommended next package: AOI 0.3.0a2 final PyPI upload + MCP Registry publish.

Before upload, rerun tests, marker sync, build/twine check, package-data audit, and MCP publisher validate. Upload must remain an explicit local action with interactive token entry and `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES`. MCP Registry publish must remain an explicit local action after PyPI verification and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.
""",
    )


def _openapi_paths() -> dict[str, Any]:
    payload = read_json(Path("api") / "openapi.json")
    paths = payload.get("paths", {}) if isinstance(payload.get("paths"), dict) else {}
    return paths


def run_agent_surface_audit(write_result: bool = True) -> dict[str, Any]:
    root = repo_root()
    card = read_json(CAPABILITY_CARD_PATH)
    manifest = get_mcp_tool_manifest()
    manifest_tools = {tool["name"]: tool for tool in manifest.get("tools", []) if isinstance(tool, dict)}
    openapi_paths = _openapi_paths()
    missing_rest = [path for path in REST_PATHS if path not in openapi_paths]
    missing_mcp = [name for name in MCP_TOOLS if name not in manifest_tools]
    non_read_only = [name for name in MCP_TOOLS if name in manifest_tools and manifest_tools[name].get("read_only") is not True]
    paths_to_scan = [
        root / "agent_discovery" / "CAPABILITY_CARD.md",
        root / "agent_discovery" / "AGENT_DISCOVER_MODE.md",
        root / "agent_discovery" / "AGENT_PREFLIGHT_MODE.md",
        root / "docs" / "aoi_agent_rest_api.md",
        root / "docs" / "aoi_agent_mcp_tools.md",
        root / "docs" / "aoi_agent_surface_contract.md",
    ]
    findings = scan_paths([path for path in paths_to_scan if path.exists()])
    private_findings = [item for item in findings if item["kind"] == "private_kernel_value"]
    overclaims = [item for item in findings if item["kind"] == "overclaim"]
    card_missing = validate_capability_card(card)

    if private_findings:
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
    elif overclaims:
        decision = "BLOCK_OVERCLAIM"
    elif missing_rest:
        decision = "HOLD_ENDPOINT_WIRING_INCOMPLETE"
    elif missing_mcp or non_read_only:
        decision = "HOLD_MCP_WIRING_INCOMPLETE"
    elif card_missing:
        decision = "HOLD_ENDPOINT_WIRING_INCOMPLETE"
    else:
        decision = "PASS_AGENT_SURFACES_READY_FOR_030A2_UPLOAD"

    result = {
        "schema": "AOI_AgentSurfaceAudit/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "rest_paths_expected": REST_PATHS,
        "missing_rest_paths": missing_rest,
        "mcp_tools_expected": MCP_TOOLS,
        "missing_mcp_tools": missing_mcp,
        "non_read_only_mcp_tools": non_read_only,
        "openapi_regenerated": not missing_rest,
        "mcp_manifest_regenerated": not missing_mcp,
        "capability_card_valid": not card_missing,
        "claim_boundary_visible": True,
        "overclaim_findings": overclaims,
        "private_kernel_findings": private_findings,
        "external_action_authorization": False,
        "external_api_used": False,
        "live_mcp_call_used": False,
        "pypi_upload_performed": False,
        "mcp_registry_publish_performed": False,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
        _write_surface_public_outputs(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_agent_surface_audit()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"agent_surface_audit: {result['decision']} rest_missing={len(result['missing_rest_paths'])} mcp_missing={len(result['missing_mcp_tools'])}")


if __name__ == "__main__":
    main()
