from ai_objective_index import mcp_registry_pre_publish_protection_gate as gate


def _payload(decision):
    return {"decision": decision, "risk_level": "MEDIUM"}


def test_pre_publish_gate_all_pass(monkeypatch):
    def fake_read_json(path):
        name = str(path)
        if "TECH" in name:
            return _payload("PASS_NO_SENSITIVE_KERNEL_EXPOSED")
        if "PUBLIC_PRIVATE" in name:
            return _payload("PASS_PUBLIC_PRIVATE_SPLIT_CLEAR")
        if "PACKAGE_ARTIFACT" in name:
            return _payload("PASS_PACKAGE_ARTIFACT_SAFE")
        if "ANTI_CLONE" in name:
            return _payload("PASS_ACCEPTABLE_PUBLIC_BETA_RISK")
        if "LICENSE" in name:
            return _payload("PASS_LICENSE_PRESENT")
        if "MANIFEST" in name:
            return _payload("PASS_MANIFEST_READY")
        return {}

    monkeypatch.setattr(gate, "_read_json", fake_read_json)
    monkeypatch.setattr(gate, "_no_secret_real_findings", lambda: True)
    monkeypatch.setattr(gate, "_claim_guard_passed", lambda: True)

    result = gate.run_mcp_registry_pre_publish_protection_gate(write_result=False)

    assert result["decision"] == "PASS_READY_FOR_MCP_REGISTRY_AFTER_PROTECTION"


def test_pre_publish_gate_package_artifact_block(monkeypatch):
    monkeypatch.setattr(gate, "_read_json", lambda path: {"decision": "BLOCK_SENSITIVE_ARTIFACT_IN_PACKAGE"} if "PACKAGE_ARTIFACT" in str(path) else _payload("PASS_PUBLIC_PRIVATE_SPLIT_CLEAR"))
    monkeypatch.setattr(gate, "_no_secret_real_findings", lambda: True)
    monkeypatch.setattr(gate, "_claim_guard_passed", lambda: True)

    result = gate.run_mcp_registry_pre_publish_protection_gate(write_result=False)

    assert result["decision"] == "BLOCK_PACKAGE_ARTIFACT_SENSITIVE"


def test_pre_publish_gate_license_review_holds(monkeypatch):
    def fake_read_json(path):
        if "LICENSE" in str(path):
            return _payload("HOLD_LICENSE_REVIEW_RECOMMENDED")
        if "TECH" in str(path):
            return _payload("PASS_NO_SENSITIVE_KERNEL_EXPOSED")
        if "PUBLIC_PRIVATE" in str(path):
            return _payload("PASS_PUBLIC_PRIVATE_SPLIT_CLEAR")
        if "PACKAGE_ARTIFACT" in str(path):
            return _payload("PASS_PACKAGE_ARTIFACT_SAFE")
        if "ANTI_CLONE" in str(path):
            return _payload("PASS_ACCEPTABLE_PUBLIC_BETA_RISK")
        if "MANIFEST" in str(path):
            return _payload("PASS_MANIFEST_READY")
        return {}

    monkeypatch.setattr(gate, "_read_json", fake_read_json)
    monkeypatch.setattr(gate, "_no_secret_real_findings", lambda: True)
    monkeypatch.setattr(gate, "_claim_guard_passed", lambda: True)

    result = gate.run_mcp_registry_pre_publish_protection_gate(write_result=False)

    assert result["decision"] == "HOLD_LICENSE_REVIEW"
