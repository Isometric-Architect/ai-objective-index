from ai_objective_index.portfolio.pilot_dry_run_router import route_sample_intake_packets
from ai_objective_index.portfolio.pilot_intake_packet import PilotIntakePacket, ProvidedArtifact
from ai_objective_index.portfolio.pilot_vertical_router import route_intake_packet


def test_dry_run_router_maps_all_three_samples():
    routes = route_sample_intake_packets(ensure_samples=True)
    assert routes["agentsec"].selected_vertical == "agentsec"
    assert routes["qira"].selected_vertical == "qira"
    assert routes["datacapsule"].selected_vertical == "datacapsule"


def test_dry_run_router_unknown_holds_manual_triage():
    packet = PilotIntakePacket(
        intake_id="intake-unknown",
        pilot_label="unknown",
        provided_artifact=ProvidedArtifact(artifact_type="unknown"),
    )
    route = route_intake_packet(packet)
    assert route.selected_vertical == "hold_manual_triage"
