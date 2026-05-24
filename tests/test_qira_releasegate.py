from ai_objective_index.qira.models import PatchCandidate
from ai_objective_index.qira.releasegate import build_behavior_contract, build_release_gate_report, sample_release_gate_report


def test_scoped_local_pass_allows_draft_and_pr_but_not_merge_or_deploy():
    report = sample_release_gate_report()

    assert report.decision_token == "PASS_CONTRACT_SCOPED"
    assert report.action_license.patch_draft == "ALLOW"
    assert report.action_license.pr_open == "ALLOW"
    assert report.action_license.merge == "HOLD"
    assert report.action_license.deploy == "BLOCK"
    assert report.receipt.can_authorize_deploy is False


def test_unsupported_claim_blocks_action_license():
    contract = build_behavior_contract("change docs", expected_behavior=["docs updated"])
    patch = PatchCandidate(
        patch_id="patch-overclaim",
        contract_id=contract.contract_id,
        summary="claims too much",
        changed_files=["README.md"],
        tests_passed=True,
        test_summary="local fixture pass",
        evidence_origin="local_fixture",
        declared_claims=["This patch is production-ready and verified."],
    )

    report = build_release_gate_report(contract, patch)

    assert report.decision_token == "BLOCK_ACTION_OVERCLAIM"
    assert report.action_license.pr_open == "BLOCK"
    assert report.summary["unsupported_claim_count"] == 1


def test_forbidden_path_blocks_patch():
    contract = build_behavior_contract("change config", expected_behavior=["config remains local"])
    patch = PatchCandidate(
        patch_id="patch-path",
        contract_id=contract.contract_id,
        summary="touches forbidden file",
        changed_files=["../.env"],
        tests_passed=True,
        test_summary="local fixture pass",
        evidence_origin="local_fixture",
    )

    report = build_release_gate_report(contract, patch)

    assert report.decision_token == "BLOCK_PATCH_PATH_ESCAPE"
    assert report.action_license.deploy == "BLOCK"


def test_missing_contract_evidence_holds():
    contract = build_behavior_contract("unclear task")
    patch = PatchCandidate(patch_id="patch-hold", contract_id=contract.contract_id, summary="unclear")

    report = build_release_gate_report(contract, patch)

    assert report.decision_token == "HOLD_NEEDS_CONTRACT"
    assert report.action_license.pr_open == "HOLD"
    assert "expected_behavior" in report.receipt.residual_ledger.missing_evidence
