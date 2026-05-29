from ai_objective_index.portfolio.residualops_vertical_matrix import build_vertical_matrix


def test_vertical_matrix_has_three_rows():
    matrix = build_vertical_matrix()
    assert matrix["row_count"] == 3
    assert [row["vertical_id"] for row in matrix["rows"]] == ["agentsec", "qira", "datacapsule"]
    assert all(row["external_action_used"] is False for row in matrix["rows"])
