from ai_objective_index import public_launch_claim_audit as audit


def _target(name: str):
    return audit._repo_root() / "tests" / name


def test_public_launch_claim_audit_detects_positive_claim():
    target = _target("__tmp_8i_positive_claim.md")
    try:
        target.write_text("These are verified MCP servers.\n", encoding="utf-8")
        result = audit.run_public_launch_claim_audit(files=[target], write_result=False)
        assert result["overall_token"] == "HOLD"
        assert result["risky_phrase_count"] > 0
    finally:
        if target.exists():
            target.unlink()


def test_public_launch_claim_audit_ignores_forbidden_context():
    target = _target("__tmp_8i_forbidden_context.md")
    try:
        target.write_text("Do not claim verified MCP servers or security certified tools.\n", encoding="utf-8")
        result = audit.run_public_launch_claim_audit(files=[target], write_result=False)
        assert result["overall_token"] == "PASS"
        assert result["risky_phrase_count"] == 0
    finally:
        if target.exists():
            target.unlink()
