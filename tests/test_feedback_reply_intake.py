from pathlib import Path

from ai_objective_index.portfolio.feedback_reply_intake import package_feedback_replies
from ai_objective_index.portfolio.feedback_reply_packet import sample_packet_paths


def test_sample_intake_generates_four_reply_packets():
    result = package_feedback_replies(sample=True)
    assert len(result["packets"]) == 4
    assert {item["related_vertical"] for item in result["packets"]} == {"agentsec", "qira", "datacapsule", "portfolio"}
    for path in sample_packet_paths().values():
        assert Path(path).exists()


def test_local_input_intake(tmp_path):
    reply = tmp_path / "reply.md"
    reply.write_text("I consent to local review. Please run a second local pass for this tool manifest.", encoding="utf-8")
    result = package_feedback_replies(input_path=str(reply))
    assert len(result["packets"]) == 1
    assert result["packets"][0]["source"] == "local_file"
