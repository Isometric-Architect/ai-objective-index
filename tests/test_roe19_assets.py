from pathlib import Path

from ai_objective_index.portfolio.feedback_reply_intake import package_feedback_replies
from ai_objective_index.portfolio.roe19_feedback_reply_gate import run_roe19_gate


def test_roe19_docs_and_outputs_exist():
    package_feedback_replies(sample=True)
    run_roe19_gate()
    expected = [
        "docs/portfolio/roe19_feedback_reply_packet_intake.md",
        "docs/portfolio/feedback_reply_workflow.md",
        "docs/portfolio/feedback_reply_packet.md",
        "docs/portfolio/feedback_reply_classification.md",
        "docs/portfolio/feedback_reply_triage.md",
        "docs/portfolio/feedback_reply_memory_candidate.md",
        "docs/portfolio/feedback_reply_second_run_candidate.md",
        "docs/portfolio/feedback_reply_claim_boundaries.md",
        "docs/portfolio/feedback_reply_operator_checklist.md",
        "feedback_replies/FEEDBACK_REPLY_PACKET_SAMPLE_AGENTSEC.json",
        "feedback_replies/FEEDBACK_REPLY_PACKET_SAMPLE_QIRA.json",
        "feedback_replies/FEEDBACK_REPLY_PACKET_SAMPLE_DATACAPSULE.json",
        "feedback_replies/FEEDBACK_REPLY_PACKET_SAMPLE_PORTFOLIO.json",
        "public_launch/roe19/ROE19_FEEDBACK_REPLY_GATE_RESULT.json",
        "public_launch/roe19/ROE19_FEEDBACK_REPLY_SUMMARY.md",
        "public_launch/roe19/ROE19_NEXT_ACTIONS.md",
    ]
    for path in expected:
        assert Path(path).exists(), path
