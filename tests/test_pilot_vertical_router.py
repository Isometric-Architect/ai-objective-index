from ai_objective_index.portfolio.pilot_intake_packet import (
    IntakeOwnerConsent,
    PilotIntakePacket,
    ProvidedArtifact,
)
from ai_objective_index.portfolio.pilot_vertical_router import route_intake_packet


def packet_for(artifact_type: str, consent: str = "sample_fixture") -> PilotIntakePacket:
    return PilotIntakePacket(
        intake_id=f"intake-{artifact_type}",
        pilot_label="sample",
        requested_vertical="auto_route",
        owner_consent=IntakeOwnerConsent(status=consent),
        provided_artifact=ProvidedArtifact(artifact_type=artifact_type),  # type: ignore[arg-type]
    )


def test_mcp_manifest_routes_to_agentsec():
    route = route_intake_packet(packet_for("mcp_manifest"))
    assert route.selected_vertical == "agentsec"
    assert route.can_generate_pilot_receipt is True


def test_pr_diff_routes_to_qira():
    route = route_intake_packet(packet_for("pr_diff"))
    assert route.selected_vertical == "qira"


def test_dataset_manifest_routes_to_datacapsule():
    route = route_intake_packet(packet_for("dataset_manifest"))
    assert route.selected_vertical == "datacapsule"


def test_unknown_routes_to_manual_triage():
    route = route_intake_packet(packet_for("unknown"))
    assert route.selected_vertical == "hold_manual_triage"
    assert route.can_generate_pilot_receipt is False


def test_missing_consent_blocks():
    route = route_intake_packet(packet_for("mcp_manifest", consent="unknown"))
    assert route.selected_vertical == "block_insufficient_consent"


def test_forbidden_action_blocks():
    packet = packet_for("mcp_manifest")
    packet.allowed_review_scope.github_api_call = True
    route = route_intake_packet(packet)
    assert route.selected_vertical == "block_forbidden_artifact"
