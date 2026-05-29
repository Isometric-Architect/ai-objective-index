import json
from pathlib import Path

from ai_objective_index.portfolio.agentsec_pilot_packager import RECEIPT_PATH, package_agentsec_pilot
from ai_objective_index.portfolio.roe8_agentsec_pilot_gate import GATE_RESULT_PATH, run_roe8_gate


def test_roe8_gate_passes_safe_sample():
    package_agentsec_pilot(sample=True)
    result = run_roe8_gate(write_result=True)

    assert result["decision"] == "PASS_FIRST_AGENTSEC_PILOT_RECEIPT_READY"
    assert result["redaction_decision"] == "PASS_REDACTED"
    assert result["live_mcp_called"] is False
    assert result["external_tool_executed"] is False
    assert Path(GATE_RESULT_PATH).exists()


def test_roe8_gate_blocks_overclaim_fixture():
    package_agentsec_pilot(sample=True)
    path = Path(RECEIPT_PATH)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["project_label"] = "verified capability"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        result = run_roe8_gate(write_result=False, ensure_sample=False)

        assert result["decision"] == "BLOCK_OVERCLAIM"
    finally:
        package_agentsec_pilot(sample=True)
        run_roe8_gate(write_result=True)
