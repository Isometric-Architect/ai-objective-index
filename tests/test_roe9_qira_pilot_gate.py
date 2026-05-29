import json
from pathlib import Path

from ai_objective_index.portfolio.qira_pilot_packager import RECEIPT_PATH, package_qira_pilot
from ai_objective_index.portfolio.roe9_qira_pilot_gate import GATE_RESULT_PATH, run_roe9_gate


def test_roe9_gate_passes_safe_sample():
    package_qira_pilot(sample=True)
    result = run_roe9_gate(write_result=True)

    assert result["decision"] == "PASS_FIRST_QIRA_PILOT_RECEIPT_READY"
    assert result["redaction_decision"] == "PASS_REDACTED"
    assert result["github_api_used"] is False
    assert result["external_repo_modified"] is False
    assert Path(GATE_RESULT_PATH).exists()


def test_roe9_gate_blocks_overclaim_fixture():
    package_qira_pilot(sample=True)
    path = Path(RECEIPT_PATH)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["task_packet"]["task_title"] = "production ready verified code"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        result = run_roe9_gate(write_result=False, ensure_sample=False)

        assert result["decision"] == "BLOCK_OVERCLAIM"
    finally:
        package_qira_pilot(sample=True)
        run_roe9_gate(write_result=True)


def test_roe9_gate_blocks_merge_deploy_authorization_fixture():
    package_qira_pilot(sample=True)
    path = Path(RECEIPT_PATH)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["claim_boundary"]["no_deploy_authorization"] = False
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        result = run_roe9_gate(write_result=False, ensure_sample=False)

        assert result["decision"] == "BLOCK_MERGE_OR_DEPLOY_AUTHORIZATION"
    finally:
        package_qira_pilot(sample=True)
        run_roe9_gate(write_result=True)
