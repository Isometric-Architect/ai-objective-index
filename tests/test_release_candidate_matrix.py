from ai_objective_index.release_candidate_matrix import build_release_candidate_matrix, save_release_candidate_matrix


def test_release_candidate_matrix_includes_required_surfaces():
    result = build_release_candidate_matrix()
    path = save_release_candidate_matrix(result)
    surfaces = {row["surface"] for row in result["surfaces"]}

    assert path.exists()
    assert result["overall_token"] in {"PASS", "HOLD"}
    for expected in {
        "Core Engine",
        "MCP tools",
        "MCP compat search/fetch",
        "REST API",
        "OpenAPI",
        "HF demo assets",
        "HF dataset draft",
        "Benchmark reports",
        "Registry intake",
        "public_beta_mcp dataset",
        "Release pack",
        "Claim audit",
        "Manual publish checklist",
    }:
        assert expected in surfaces
    assert all("status" in row and "evidence_file" in row for row in result["surfaces"])
