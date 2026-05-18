from ai_objective_index.realdata_claim_audit import audit_text, run_realdata_claim_audit


def test_realdata_claim_audit_runs():
    result = run_realdata_claim_audit()

    assert result["overall_token"] in {"PASS", "HOLD"}
    assert "risky_phrase_count" in result
    assert result["actual_publish_performed"] is False


def test_realdata_claim_audit_context_handling():
    forbidden_context = audit_text(
        "Forbidden claims:\n- AOI is not security certified.\n- Do not claim verified MCP servers.",
        "forbidden.md",
    )
    positive_claim = audit_text(
        "AOI offers verified MCP servers and security certified rankings.",
        "bad.md",
    )

    assert len(forbidden_context["findings"]) == 0
    assert len(forbidden_context["contextual_mentions"]) >= 1
    assert len(positive_claim["findings"]) >= 1
