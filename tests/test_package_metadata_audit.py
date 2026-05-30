from ai_objective_index.package_metadata_audit import (
    MCP_MARKER,
    find_token_like_strings,
    readme_has_mcp_marker,
    run_package_metadata_audit,
    version_is_pep440,
)


def test_package_metadata_audit_detects_marker_and_version():
    result = run_package_metadata_audit(write_result=False)

    assert result["checks"]["readme_mcp_marker"] is True
    assert result["checks"]["version_pep440"] is True
    assert result["version"] in {"0.2.0", "0.3.0a1", "0.3.0a2"}


def test_package_metadata_helpers_detect_missing_marker_and_tokens():
    assert readme_has_mcp_marker(MCP_MARKER)
    assert not readme_has_mcp_marker("# README")
    assert find_token_like_strings("token = ghp_abc123")
    assert version_is_pep440("0.2.0")
    assert version_is_pep440("0.3.0a1")
