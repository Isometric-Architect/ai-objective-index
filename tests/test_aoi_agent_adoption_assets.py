import json
from pathlib import Path

from ai_objective_index.agent_adoption import repo_root
from ai_objective_index.agent_adoption.agent_adoption_packager import package_agent_adoption


def test_agent_adoption_docs_and_assets_exist():
    package_agent_adoption()
    root = repo_root()
    required = [
        "agent_discovery/CAPABILITY_CARD.md",
        "agent_discovery/WHEN_TO_USE_AOI.md",
        "agent_discovery/WHEN_NOT_TO_USE_AOI.md",
        "agent_discovery/AGENT_CLAIM_BOUNDARY.md",
        "agent_discovery/PRIVATE_KERNEL_NONDISCLOSURE.md",
        "examples/agent_prompts/discover_mcp_candidates.md",
        "examples/agent_prompts/preflight_mcp_candidate.md",
        "docs/aoi_agent_native_discovery.md",
        "docs/aoi_agent_preflight.md",
        "docs/aoi_private_kernel_non_disclosure.md",
    ]

    for relative in required:
        assert (root / relative).exists()


def test_agent_schemas_exist_and_are_json():
    package_agent_adoption()
    schema_dir = repo_root() / "schemas" / "agent"

    schema_files = [
        "aoi_capability_card.schema.json",
        "aoi_agent_discover_request.schema.json",
        "aoi_agent_discover_response.schema.json",
        "aoi_agent_preflight_request.schema.json",
        "aoi_agent_preflight_response.schema.json",
        "aoi_agent_output_contract.schema.json",
        "residualops_extension_map.schema.json",
    ]
    for filename in schema_files:
        payload = json.loads((schema_dir / filename).read_text(encoding="utf-8"))
        assert payload["type"] == "object"


def test_agent_openapi_examples_are_examples_only():
    package_agent_adoption()
    text = (repo_root() / "agent_discovery" / "OPENAPI_AGENT_EXAMPLES.md").read_text(encoding="utf-8")

    assert "AOI-AGENT-ADOPTION-2 wires the read-only local REST shapes" in text
    assert (repo_root() / Path("api/vnext/examples/agent/preflight_response.json")).exists()
    assert (repo_root() / Path("api/vnext/examples/agent/capability_card_response.json")).exists()
    assert (repo_root() / Path("api/vnext/examples/agent/adoption_status_response.json")).exists()
