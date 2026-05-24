import json
from pathlib import Path

from ai_objective_index.qira.ci_evidence_cli import (
    AUGMENTED_PACKET_PATH,
    REVIEW_RESULT_PATH,
    SAMPLE_CI_EVIDENCE_PATH,
    SAMPLE_PACKET_PATH,
    VALIDATION_RESULT_PATH,
    run_sample,
)


def test_qira6_run_sample_writes_outputs():
    result = run_sample()

    assert result["decision"] == "PASS_QIRA6_REVIEW"
    assert result["validation_decision"] == "PASS_CI_EVIDENCE_ACCEPTED"
    assert Path(SAMPLE_PACKET_PATH).exists()
    assert Path(SAMPLE_CI_EVIDENCE_PATH).exists()
    assert Path(VALIDATION_RESULT_PATH).exists()
    assert Path(AUGMENTED_PACKET_PATH).exists()
    assert Path(REVIEW_RESULT_PATH).exists()

    review = json.loads(Path(REVIEW_RESULT_PATH).read_text(encoding="utf-8"))
    assert review["commands_executed_by_qira"] is False
    assert review["github_api_used_by_qira"] is False
    assert review["release_gate_review"]["release_gate_decision"] == "PASS_CONTRACT_SCOPED"
