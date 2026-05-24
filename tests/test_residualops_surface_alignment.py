from pathlib import Path

from ai_objective_index.residualops_surface_alignment import (
    ACTIVE_WORKFLOW_NAMES,
    build_vertical_surface_inventory,
    run_surface_alignment_gate,
)


def test_vertical_surface_inventory_passes_current_repo():
    result = build_vertical_surface_inventory()

    assert result["decision"] == "PASS_VERTICAL_SURFACES_PRESENT"
    assert result["vertical_count"] == 3
    assert result["active_workflow_findings"] == []


def test_vertical_surface_inventory_detects_missing_surface(tmp_path: Path):
    result = build_vertical_surface_inventory(root=tmp_path)

    assert result["decision"] == "HOLD_VERTICAL_SURFACE_MISSING"
    assert result["missing_paths"]


def test_vertical_surface_inventory_blocks_active_workflow(tmp_path: Path):
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / next(iter(ACTIVE_WORKFLOW_NAMES))).write_text("name: active\n", encoding="utf-8")

    result = build_vertical_surface_inventory(root=tmp_path)

    assert result["decision"] == "BLOCK_ACTIVE_WORKFLOW_CREATED"
    assert result["active_workflow_findings"]


def test_surface_alignment_gate_passes_current_repo():
    result = run_surface_alignment_gate(write_result=False)

    assert result["decision"] == "PASS_ROE1_SURFACE_ALIGNED"
    assert result["safe_to_continue_parallel_verticals"] is True
    assert result["external_actions_performed"] is False
