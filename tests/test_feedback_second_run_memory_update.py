from ai_objective_index.portfolio.feedback_second_run_memory_update import build_memory_update, memory_update_to_jsonable


def test_memory_update_records_incorporated_and_skipped_statuses():
    memory = build_memory_update(
        "bridge-test",
        [{"reply_id": "reply-agentsec", "vertical": "agentsec", "incorporation_summary": "incorporated"}],
        [{"reply_id": "reply-qira", "vertical": "qira", "reason": "HOLD_NEEDS_ARTIFACT", "next_actions": ["collect artifact"]}],
    )
    payload = memory_update_to_jsonable(memory)
    statuses = {entry["reply_id"]: entry["new_status"] for entry in payload["updated_entries"]}
    assert statuses["reply-agentsec"] == "incorporated"
    assert statuses["reply-qira"] == "skipped_missing_artifact"
