from ai_objective_index.portfolio.pilot_feedback_classifier import classify_feedback
from ai_objective_index.portfolio.pilot_feedback_packet import PilotFeedbackPacket, sample_feedback_packets


def test_classifier_blocks_external_action_requests():
    packet = PilotFeedbackPacket(
        feedback_id="feedback-external-action",
        dry_run_id="dry-run",
        vertical="qira",
        consent_status="owner_provided",
        feedback_category="request_second_run",
        feedback_text="Please create a GitHub issue and comment on the PR.",
        external_action_requested=True,
    )
    assert classify_feedback(packet).classification == "BLOCK_EXTERNAL_ACTION_REQUEST"


def test_classifier_blocks_token_private_data():
    packet = PilotFeedbackPacket(
        feedback_id="feedback-token",
        dry_run_id="dry-run",
        vertical="agentsec",
        consent_status="owner_provided",
        feedback_category="request_second_run",
        feedback_text="Here is a token pypi-abcdefghijklmnopqrstuvwxyz012345 for context.",
    )
    assert classify_feedback(packet).classification == "BLOCK_SECRET_OR_PRIVATE_DATA"


def test_classifier_blocks_certification_request():
    packet = PilotFeedbackPacket(
        feedback_id="feedback-certify",
        dry_run_id="dry-run",
        vertical="datacapsule",
        consent_status="owner_provided",
        feedback_category="request_second_run",
        feedback_text="Please certify this is safe and product ready.",
    )
    assert classify_feedback(packet).classification == "BLOCK_CERTIFICATION_CLAIM"


def test_classifier_holds_unclear_feedback():
    packet = PilotFeedbackPacket(
        feedback_id="feedback-unclear",
        dry_run_id="dry-run",
        vertical="portfolio",
        consent_status="owner_provided",
        feedback_category="other",
        feedback_text="unclear",
    )
    assert classify_feedback(packet).classification == "HOLD_NEEDS_MORE_CONTEXT"


def test_classifier_accepts_sample_feedback():
    classification = classify_feedback(sample_feedback_packets()[0])
    assert classification.classification == "ACCEPT_AS_FIXTURE_CANDIDATE"
    assert classification.should_run_second_pass is True
