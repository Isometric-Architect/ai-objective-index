from pathlib import Path

from ai_objective_index import aoi_030a2_final_preflight as preflight
from ai_objective_index.aoi_030a2_marker_sync import CANONICAL_MCP_NAME, MCP_MARKER, PACKAGE_NAME, TARGET_VERSION


def _good_json(path: Path):
    normalized = str(path).replace("\\", "/")
    if normalized.endswith(".mcp/server.json"):
        return {
            "name": CANONICAL_MCP_NAME,
            "version": TARGET_VERSION,
            "packages": [{"registryType": "pypi", "identifier": PACKAGE_NAME, "version": TARGET_VERSION}],
        }
    if normalized.endswith("CAPABILITY_CARD.json"):
        return {"version": TARGET_VERSION}
    if normalized.endswith("api/openapi.json"):
        return {"paths": {route: {} for route in preflight.REST_PATHS}}
    if normalized.endswith("data/generated_mcp_tools_manifest.json"):
        return {"tools": [{"name": tool} for tool in preflight.MCP_TOOLS]}
    return {}


def _patch_good(monkeypatch):
    monkeypatch.setattr(preflight, "run_marker_sync", lambda write_result=True: {"decision": "PASS_MARKER_SYNCED_030A2"})
    monkeypatch.setattr(preflight, "current_marker_state", lambda: {})
    monkeypatch.setattr(preflight, "read_json", _good_json)
    monkeypatch.setattr(preflight, "read_text", lambda path: MCP_MARKER)
    monkeypatch.setattr(preflight, "write_final_build_result", lambda: {"decision": "PASS_FINAL_BUILD_READY"})
    monkeypatch.setattr(preflight, "committed_release_dist_files", lambda: [])
    monkeypatch.setattr(preflight, "committed_mcp_publisher_binaries", lambda: [])
    monkeypatch.setattr(preflight, "token_file_candidates", lambda: [])
    monkeypatch.setattr(preflight, "pypirc_exists", lambda: False)


def _run(monkeypatch):
    _patch_good(monkeypatch)
    return preflight.run_final_preflight(
        package_data_runner=lambda write_result=True: {"decision": "PASS_AGENT_PACKAGE_DATA_READY"},
        surface_runner=lambda write_result=True: {"decision": "PASS_AGENT_SURFACES_READY_FOR_030A2_UPLOAD"},
        no_secrets_runner=lambda: {"overall_token": "HOLD", "finding_count": 0, "warning_count": 3},
        claim_runner=lambda: {"overall_token": "PASS", "risky_phrase_count": 0},
        tech_runner=lambda write_result=True: {"decision": "PASS_NO_SENSITIVE_KERNEL_EXPOSED"},
        alignment_runner=lambda write_result=True: {"decision": "PASS_PUBLIC_PRIVATE_ALIGNMENT"},
        write_result=False,
    )


def test_final_preflight_passes_when_distribution_inputs_are_ready(monkeypatch):
    result = _run(monkeypatch)

    assert result["decision"] == "PASS_READY_FOR_FINAL_PYPI_UPLOAD"


def test_final_preflight_blocks_version_mismatch(monkeypatch):
    monkeypatch.setattr(preflight, "_pyproject_version", lambda: "0.3.0a1")

    result = _run(monkeypatch)

    assert result["decision"] != "PASS_READY_FOR_FINAL_PYPI_UPLOAD"
    assert result["checks"]["pyproject_version"] is False


def test_final_preflight_blocks_marker_mismatch(monkeypatch):
    _patch_good(monkeypatch)
    monkeypatch.setattr(preflight, "read_text", lambda path: "")

    result = preflight.run_final_preflight(
        package_data_runner=lambda write_result=True: {"decision": "PASS_AGENT_PACKAGE_DATA_READY"},
        surface_runner=lambda write_result=True: {"decision": "PASS_AGENT_SURFACES_READY_FOR_030A2_UPLOAD"},
        no_secrets_runner=lambda: {"overall_token": "PASS", "finding_count": 0, "warning_count": 0},
        claim_runner=lambda: {"overall_token": "PASS", "risky_phrase_count": 0},
        tech_runner=lambda write_result=True: {"decision": "PASS_NO_SENSITIVE_KERNEL_EXPOSED"},
        alignment_runner=lambda write_result=True: {"decision": "PASS_PUBLIC_PRIVATE_ALIGNMENT"},
        write_result=False,
    )

    assert result["decision"] != "PASS_READY_FOR_FINAL_PYPI_UPLOAD"
    assert result["checks"]["readme_marker"] is False

