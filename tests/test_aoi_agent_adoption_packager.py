from pathlib import Path

from ai_objective_index.agent_adoption import repo_root
from ai_objective_index.agent_adoption.agent_adoption_audit import run_agent_adoption_audit
from ai_objective_index.agent_adoption.agent_adoption_packager import package_agent_adoption


def test_agent_adoption_packager_generates_pack():
    result = package_agent_adoption()

    assert result["decision"] == "PASS_AGENT_DISCOVERY_PACK_GENERATED"
    assert result["discover_candidate_count"] == 3
    assert result["preflight_decision"] == "HOLD_MISSING_PERMISSION_SCOPE"
    assert result["pypi_upload_performed"] is False
    assert result["mcp_registry_publish_performed"] is False


def test_agent_adoption_audit_passes_generated_pack():
    package_agent_adoption()
    audit = run_agent_adoption_audit(write_result=False)

    assert audit["decision"] == "PASS_AGENT_NATIVE_DISCOVERY_READY"
    assert audit["private_kernel_not_disclosed"] is True
    assert audit["external_api_used"] is False
    assert audit["live_mcp_call_used"] is False


def test_agent_adoption_core_files_exist():
    package_agent_adoption()
    root = repo_root()

    for path in [
        Path("agent_discovery") / "CAPABILITY_CARD.json",
        Path("agent_discovery") / "AGENT_DISCOVER_MODE.md",
        Path("api") / "vnext" / "examples" / "agent" / "discover_response.json",
        Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_ADOPTION_AUDIT_RESULT.json",
    ]:
        assert (root / path).exists()

