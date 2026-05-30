from ai_objective_index.portfolio.feedback_reply_classifier import classify_feedback_reply
from ai_objective_index.portfolio.feedback_reply_packet import FeedbackReplyPacket
from ai_objective_index.portfolio.feedback_reply_router import route_feedback_reply


def _route(text: str, vertical: str = "unknown"):
    packet = FeedbackReplyPacket(
        reply_id=f"reply-{vertical}",
        reply_text_redacted=text,
        related_vertical=vertical,
        consent_signal="sample_fixture",
        requested_action="clarify",
    )
    return route_feedback_reply(packet, classify_feedback_reply(packet))


def test_router_maps_tool_feedback_to_agentsec():
    assert _route("The tool manifest permission explanation is unclear.").selected_vertical == "agentsec"


def test_router_maps_code_feedback_to_qira():
    assert _route("The patch and CI evidence request should be clearer.").selected_vertical == "qira"


def test_router_maps_dataset_feedback_to_datacapsule():
    assert _route("The dataset license and privacy boundary is unclear.").selected_vertical == "datacapsule"


def test_router_maps_dashboard_feedback_to_portfolio():
    assert _route("The dashboard readout should show next steps.").selected_vertical == "portfolio"
