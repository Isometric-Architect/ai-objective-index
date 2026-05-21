from ai_objective_index import mcp_registry_release_audit as audit


def test_release_audit_publish_and_verify_pass(monkeypatch):
    def fake_read_json(path):
        name = str(path)
        if "PUBLISH_RESULT" in name:
            return {"result_token": "PUBLISH_SUCCESS", "submission_performed": True}
        if "POST_PUBLISH_VERIFY" in name:
            return {"decision": "PASS_REGISTRY_ENTRY_FOUND"}
        if "MANIFEST_FINAL" in name:
            return {"decision": "PASS_MANIFEST_READY"}
        if "REAL_PYPI" in name:
            return {"decision": "PASS_REAL_PYPI_RELEASE_VERIFIED"}
        return {}

    monkeypatch.setattr(audit, "_read_json", fake_read_json)
    monkeypatch.setattr(audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(audit, "_claim_guard_passed", lambda: True)

    result = audit.run_mcp_registry_release_audit(write_result=False)

    assert result["decision"] == "PASS_MCP_REGISTRY_RELEASE_RECORDED"


def test_release_audit_missing_publish_holds(monkeypatch):
    monkeypatch.setattr(audit, "_read_json", lambda path: {"decision": "PASS_MANIFEST_READY"})
    monkeypatch.setattr(audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(audit, "_claim_guard_passed", lambda: True)

    result = audit.run_mcp_registry_release_audit(write_result=False)

    assert result["decision"] == "HOLD_PUBLISH_NOT_CONFIRMED"


def test_release_audit_overclaim_blocks(monkeypatch):
    monkeypatch.setattr(audit, "_read_json", lambda path: {"decision": "BLOCK_OVERCLAIM"})
    monkeypatch.setattr(audit, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(audit, "_claim_guard_passed", lambda: False)

    result = audit.run_mcp_registry_release_audit(write_result=False)

    assert result["decision"] == "BLOCK_OVERCLAIM"
