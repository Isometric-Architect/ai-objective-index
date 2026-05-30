from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from . import VERSION, timestamp, write_json, write_text
from .agent_adoption_audit import run_agent_adoption_audit
from .agent_examples_packager import write_example_artifacts
from .agent_output_contract import write_output_contract_examples
from .capability_card import build_capability_card, write_capability_card
from .discover_mode import write_sample_discover_examples
from .preflight_mode import write_sample_preflight_examples
from .residualops_extension_map import build_residualops_extension_map, extension_map_markdown


PACK_RESULT_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_DISCOVERY_PACK_RESULT.json"
SUMMARY_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_ADOPTION_SUMMARY.md"
NEXT_ACTIONS_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_ADOPTION_NEXT_ACTIONS.md"
CAPABILITY_CARD_RESPONSE_PATH = Path("api") / "vnext" / "examples" / "agent" / "capability_card_response.json"
ADOPTION_STATUS_RESPONSE_PATH = Path("api") / "vnext" / "examples" / "agent" / "adoption_status_response.json"


def _schema(title: str, required: list[str], properties: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {key: {"type": ["string", "array", "object", "boolean", "number", "integer", "null"]} for key in required}
    if properties:
        props.update(properties)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "type": "object",
        "required": required,
        "properties": props,
        "additionalProperties": True,
    }


def write_schemas() -> list[str]:
    schemas = {
        "aoi_capability_card.schema.json": _schema(
            "AOI Capability Card",
            ["schema", "name", "package", "version", "mcp_name", "type", "modes", "claim_boundary"],
        ),
        "aoi_agent_discover_request.schema.json": _schema(
            "AOI Agent Discover Request",
            ["schema", "objective", "query", "data_scope", "desired_capability_type", "freshness_preference"],
        ),
        "aoi_agent_discover_response.schema.json": _schema(
            "AOI Agent Discover Response",
            ["schema", "objective", "mode", "candidates", "route_decision", "missing_fields", "next_action", "must_not_claim", "freshness"],
        ),
        "aoi_agent_preflight_request.schema.json": _schema(
            "AOI Agent Preflight Request",
            ["schema", "candidate_id", "intended_use", "available_metadata", "required_permissions"],
        ),
        "aoi_agent_preflight_response.schema.json": _schema(
            "AOI Agent Preflight Response",
            ["schema", "candidate_id", "mode", "route_decision", "reason", "missing_fields", "next_action", "must_not_claim"],
        ),
        "aoi_agent_output_contract.schema.json": _schema(
            "AOI Agent Output Contract",
            ["objective", "mode", "candidates", "route_decision", "reason", "missing_fields", "next_action", "must_not_claim", "residualops_escalation", "freshness"],
        ),
        "residualops_extension_map.schema.json": _schema(
            "ResidualOps Extension Map",
            ["schema", "aoi_role", "residualops_role", "routes", "claim_boundary"],
        ),
    }
    written: list[str] = []
    for filename, payload in schemas.items():
        path = Path("schemas") / "agent" / filename
        write_json(path, payload)
        written.append(str(path).replace("\\", "/"))
    return written


def write_extension_map_artifacts() -> dict[str, Any]:
    payload = build_residualops_extension_map()
    write_json(Path("agent_discovery") / "RESIDUALOPS_EXTENSION_MAP.json", payload)
    write_text(Path("agent_discovery") / "RESIDUALOPS_EXTENSION_MAP.md", extension_map_markdown(payload))
    return payload


def write_public_summaries(result: dict[str, Any], audit: dict[str, Any]) -> None:
    write_text(
        SUMMARY_PATH,
        f"""# AOI Agent Adoption Summary

Decision: `{audit['decision']}`

AOI 0.3.0a2 now includes an agent-native discovery and preflight pack. The pack presents AOI as AI-native capability discovery plus pre-use trust routing: discover useful source-traced candidates first, preflight permission and claim boundaries second, and keep claim boundaries always visible.

| Field | Value |
| --- | --- |
| Version | `{VERSION}` |
| Capability card | `{result['capability_card']['type']}` |
| Discover candidates | `{result['discover_candidate_count']}` |
| Preflight sample decision | `{result['preflight_decision']}` |
| Audit | `{audit['decision']}` |
| PyPI upload performed | `False` |
| MCP Registry publish performed | `False` |

No external APIs, live MCP/tool calls, PyPI upload, MCP Registry publish, token handling, private-kernel disclosure, certification claim, product-readiness claim, or action authorization is included.
""",
    )
    write_text(
        NEXT_ACTIONS_PATH,
        """# AOI Agent Adoption Next Actions

Recommended next package: AOI 0.3.0a2 final PyPI upload + MCP Registry publish.

Before upload or registry publish, keep the 0.3.0a2 marker sync intact, rerun local tests/build/twine check, verify the README `mcp-name` marker in the package, and use only interactive token prompts with explicit environment confirmations.
""",
    )


def adoption_status_response() -> dict[str, Any]:
    return {
        "capability_card_present": True,
        "discover_mode_available": True,
        "preflight_mode_available": True,
        "examples_present": True,
        "private_kernel_exposed": False,
        "external_action_authorization": False,
        "pyPI_upload_performed": False,
        "mcp_registry_publish_performed": False,
        "read_only": True,
        "external_api_used": False,
        "live_mcp_call_used": False,
    }


def write_agent_surface_examples(card: dict[str, Any]) -> dict[str, Any]:
    capability_response = {
        "endpoint": "GET /v1/agents/capability-card",
        "read_only": True,
        "external_api_used": False,
        "live_mcp_call_used": False,
        "action_authorization": False,
        "capability_card": card,
    }
    status_response = adoption_status_response()
    write_json(CAPABILITY_CARD_RESPONSE_PATH, capability_response)
    write_json(ADOPTION_STATUS_RESPONSE_PATH, status_response)
    return {
        "capability_card_response": str(CAPABILITY_CARD_RESPONSE_PATH).replace("\\", "/"),
        "adoption_status_response": str(ADOPTION_STATUS_RESPONSE_PATH).replace("\\", "/"),
    }


def package_agent_adoption(write_result: bool = True) -> dict[str, Any]:
    card = write_capability_card()
    discover = write_sample_discover_examples()
    preflight = write_sample_preflight_examples()
    contract = write_output_contract_examples()
    example_counts = write_example_artifacts()
    surface_examples = write_agent_surface_examples(card)
    extension_map = write_extension_map_artifacts()
    schemas = write_schemas()
    write_json(Path("agent_discovery") / "AGENT_OUTPUT_SCHEMA_EXAMPLES.json", contract)
    write_text(
        Path("agent_discovery") / "AGENT_DISCOVERY_PACK_SUMMARY.md",
        """# AOI Agent Discovery Pack Summary

The AOI agent discovery pack gives ordinary AI agents a practical two-step workflow:

1. Discover useful source-traced candidates, including HOLD candidates with next actions.
2. Preflight a selected candidate before recommendation or use.

Claim boundary remains visible throughout: candidate is not verified, metadata is not proof, tool availability is not authorization, and route decision is not action authorization.
""",
    )

    audit = run_agent_adoption_audit(write_result=True)
    result = {
        "schema": "AOI_AgentDiscoveryPackResult/v0.1",
        "generated_at": timestamp(),
        "decision": "PASS_AGENT_DISCOVERY_PACK_GENERATED" if audit["decision"] == "PASS_AGENT_NATIVE_DISCOVERY_READY" else "HOLD_AGENT_DISCOVERY_PACK_REVIEW",
        "version": VERSION,
        "capability_card": {"name": card["name"], "type": card["type"], "modes": card["modes"]},
        "discover_candidate_count": len(discover["top_candidates"]),
        "discover_route_decision": discover["route_decision"],
        "preflight_decision": preflight["route_decision"],
        "output_contract_required_keys": contract["required_output_keys"],
        "residualops_routes": list(extension_map["routes"].keys()),
        "schema_files": schemas,
        "surface_example_files": surface_examples,
        "markdown_artifacts_written": example_counts["markdown_count"],
        "json_artifacts_written": example_counts["json_count"] + len(surface_examples),
        "audit_decision": audit["decision"],
        "private_kernel_exposed": False,
        "external_api_used": False,
        "live_mcp_call_used": False,
        "pypi_upload_performed": False,
        "mcp_registry_publish_performed": False,
    }
    if write_result:
        write_json(PACK_RESULT_PATH, result)
        write_public_summaries(result, audit)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    result = package_agent_adoption(write_result=not args.no_write)
    print(f"agent_adoption_packager: {result['decision']} discover_candidates={result['discover_candidate_count']}")


if __name__ == "__main__":
    main()
