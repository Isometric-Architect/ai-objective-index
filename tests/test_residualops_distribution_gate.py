from pathlib import Path

from ai_objective_index.residualops_distribution_gate import (
    DISTRIBUTION_GATE_PATH,
    DISTRIBUTION_MATRIX_PATH,
    active_workflow_findings,
    build_distribution_gate,
    build_distribution_matrix,
    run_distribution_split_gate,
    run_roe4_claim_audit,
)


def test_roe4_distribution_gate_passes_current_surfaces():
    result = run_distribution_split_gate(write_result=True)

    assert result["decision"] == "PASS_ROE4_DISTRIBUTION_SPLIT_READY"
    assert result["vertical_count"] == 3
    assert result["workflow_enabled"] is False
    assert result["private_kernel_exposed"] is False
    assert result["can_authorize_action"] is False
    assert Path(DISTRIBUTION_GATE_PATH).exists()
    assert Path(DISTRIBUTION_MATRIX_PATH).exists()


def test_roe4_matrix_uses_latest_opt_in_packages():
    matrix = build_distribution_matrix()

    assert {vertical["package"] for vertical in matrix["verticals"]} == {"QIRA-9", "AgentSec-8", "DataCapsule-7"}
    assert matrix["active_workflow_findings"] == []
    assert matrix["unsafe_flag_findings"] == []


def test_roe4_blocks_active_workflow_fixture(tmp_path: Path):
    workflow = tmp_path / ".github" / "workflows" / "qira9-optional-pr-review-artifact.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: active\n", encoding="utf-8")

    assert active_workflow_findings(tmp_path) == [".github/workflows/qira9-optional-pr-review-artifact.yml"]
    result = build_distribution_gate(
        root=tmp_path,
        matrix=build_distribution_matrix(tmp_path),
        claim_audit={"decision": "PASS_ROE4_CLAIM_BOUNDARY"},
        alignment={"decision": "PASS_PUBLIC_PRIVATE_ALIGNMENT"},
    )

    assert result["decision"] == "BLOCK_ROE4_ACTIVE_WORKFLOW_FOUND"


def test_roe4_claim_audit_blocks_private_kernel_fixture(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("private ranking weight: 0.82\n", encoding="utf-8")

    result = run_roe4_claim_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "BLOCK_ROE4_PRIVATE_KERNEL_LEAK"
    assert result["finding_count"] == 1


def test_roe4_claim_audit_allows_boundary_language(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("Do not claim security certified status or action authorized status.\n", encoding="utf-8")

    result = run_roe4_claim_audit(write_result=False, root=tmp_path, paths=[Path("doc.md")])

    assert result["decision"] == "PASS_ROE4_CLAIM_BOUNDARY"
