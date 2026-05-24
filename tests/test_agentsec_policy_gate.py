from pathlib import Path

from ai_objective_index.agentsec.policy_gate import (
    SAMPLE_MANIFEST_SET,
    apply_policy_profile,
    build_agentsec2_sample_outputs,
    build_policy_gate_markdown,
    build_policy_gate_result,
    developer_default_profile,
    read_manifest_set,
    strict_enterprise_profile,
)
from ai_objective_index.agentsec.manifest_scanner import scan_manifest_payload


def test_agentsec2_sample_has_allow_hold_and_block_counts():
    result = build_policy_gate_result(SAMPLE_MANIFEST_SET, developer_default_profile())

    assert result.decision == "BLOCK_AGENTSEC2_POLICY_RISK"
    assert result.packet_count == 3
    assert result.allow_count == 1
    assert result.hold_count == 1
    assert result.block_count == 1
    assert result.network_used is False
    assert result.external_tool_executed is False


def test_agentsec2_policy_never_upgrades_existing_hold():
    packet = scan_manifest_payload({"name": "no-namespace"})
    assert packet.risk_decision == "HOLD_REVIEW_REQUIRED"

    updated, hold_reasons, block_reasons = apply_policy_profile(packet, developer_default_profile())

    assert updated.risk_decision == "HOLD_REVIEW_REQUIRED"
    assert hold_reasons
    assert block_reasons == []


def test_agentsec2_policy_blocks_forbidden_action_language():
    result = build_policy_gate_result(
        [
            {
                "name": "checkout-helper",
                "id": "fixture.local/checkout-helper",
                "description": "Can complete payment.",
            }
        ],
        developer_default_profile(),
    )

    assert result.decision == "BLOCK_AGENTSEC2_POLICY_RISK"
    assert result.policy_block_reasons


def test_agentsec2_strict_profile_serializes():
    profile = strict_enterprise_profile()
    payload = profile.model_dump(mode="json", by_alias=True)

    assert payload["schema"] == "AgentSec_PolicyProfile/v0.1"
    assert payload["mode"] == "strict_enterprise"
    assert payload["public_weight_details_exposed"] is False


def test_agentsec2_read_manifest_set_file_and_directory(tmp_path):
    file_path = tmp_path / "manifest_set.json"
    file_path.write_text('[{"name":"one","id":"fixture.local/one"}]', encoding="utf-8")
    assert len(read_manifest_set(file_path)) == 1

    dir_path = tmp_path / "manifests"
    dir_path.mkdir()
    (dir_path / "a.json").write_text('{"name":"a","id":"fixture.local/a"}', encoding="utf-8")
    (dir_path / "b.json").write_text('{"name":"b","id":"fixture.local/b"}', encoding="utf-8")
    assert len(read_manifest_set(Path(dir_path))) == 2


def test_agentsec2_markdown_has_boundaries():
    result = build_policy_gate_result(SAMPLE_MANIFEST_SET, developer_default_profile())
    markdown = build_policy_gate_markdown(result)

    assert "AgentSec-2 Policy Gate Report" in markdown
    assert "External tool execution | `False`" in markdown
    assert "does not certify security" in markdown


def test_agentsec2_run_sample_writes_outputs():
    result = build_agentsec2_sample_outputs()

    assert result.packet_count == 3
    assert Path("public_launch/agentsec2/AGENTSEC2_BATCH_SCAN_RESULT.json").exists()
    assert Path("public_launch/agentsec2/AGENTSEC2_POLICY_GATE_REPORT.md").exists()
