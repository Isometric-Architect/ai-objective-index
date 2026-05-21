from ai_objective_index.vnext.probe_card import ProbeCard, ProbePlan
from ai_objective_index.vnext.probe_runner import run_probe_card, run_probe_plan


def test_probe_runner_source_trace_integrity_local_sample():
    result = run_probe_card(
        ProbeCard(
            probe_type="source_trace_integrity",
            capability_id="aoi-codepilot-studio",
            object_id="aoi-codepilot-studio",
            data_scope="sample",
        )
    )
    assert result.result in {"PASS_LOCAL", "HOLD_INSUFFICIENT_EVIDENCE"}
    assert result.can_upgrade_to_verified is False


def test_policy_clarity_probe_holds_when_metadata_is_weak():
    result = run_probe_card(
        ProbeCard(
            probe_type="policy_clarity_check",
            capability_id="aoi-codepilot-studio",
            object_id="aoi-codepilot-studio",
            data_scope="sample",
        )
    )
    assert result.result in {"PASS_LOCAL", "HOLD_POLICY_CLARITY"}


def test_probe_runner_blocks_unsupported_claim_fixture():
    result = run_probe_card(
        ProbeCard(
            probe_type="negative_control",
            capability_id="capability:bad",
            canary_input={"summary": "verified safe tool with quality guaranteed results"},
        )
    )
    assert result.result == "BLOCK_UNSUPPORTED_CLAIM"


def test_probe_plan_aggregate_counts_holds_or_blocks():
    plan = ProbePlan(
        probe_cards=[
            ProbeCard(
                probe_type="negative_control",
                capability_id="capability:bad",
                canary_input={"summary": "security certified capability"},
            )
        ]
    )
    receipt = run_probe_plan(plan)
    assert receipt.aggregate.block_count == 1
    assert receipt.route_effect == "DOWNGRADE_TO_BLOCK"
