from ai_objective_index.portfolio.second_run_executor import run_second_run


def test_second_run_feedback_memory_updates_pending_statuses():
    result = run_second_run(sample=True, write_result=True)
    entries = result["feedback_memory"]["updated_entries"]
    statuses = {entry["vertical"]: entry["new_status"] for entry in entries}
    assert statuses["agentsec"] == "incorporated"
    assert statuses["qira"] == "pending_with_followup"
    assert statuses["datacapsule"] == "incorporated"
