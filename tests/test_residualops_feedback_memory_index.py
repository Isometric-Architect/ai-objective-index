from ai_objective_index.portfolio.residualops_feedback_memory_index import build_feedback_memory_index


def test_feedback_memory_index_includes_all_three_verticals():
    index = build_feedback_memory_index()
    assert index["entry_count"] == 3
    assert {entry["vertical_id"] for entry in index["entries"]} == {"agentsec", "qira", "datacapsule"}
    assert any(entry["should_add_negative_control"] for entry in index["entries"])
    assert "add owner-consented pilot intake" in index["portfolio_next_actions"]
