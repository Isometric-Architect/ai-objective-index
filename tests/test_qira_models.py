from ai_objective_index.qira.models import BehaviorContract, PatchCandidate


def test_behavior_contract_serializes_schema_alias():
    contract = BehaviorContract(contract_id="contract-1", task="add local CLI", expected_behavior=["writes JSON"])

    payload = contract.model_dump(mode="json", by_alias=True)

    assert payload["schema"] == "QIRA_BehaviorContract/v0.1"
    assert payload["test_command_scope"]["no_network"] is True


def test_patch_candidate_defaults_to_unknown_evidence():
    patch = PatchCandidate(patch_id="patch-1", contract_id="contract-1", summary="fixture patch")

    assert patch.evidence_origin == "unknown"
    assert patch.requested_action == "patch_draft"
