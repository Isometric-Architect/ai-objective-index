from pathlib import Path


def test_agentsec1_docs_exist():
    assert Path("docs/agentsec_gate_plan.md").exists()
    assert Path("docs/agentsec1_tool_risk_packet.md").exists()
    assert Path("docs/agentsec_manifest_scanner.md").exists()
    assert Path("docs/agentsec_limitations.md").exists()


def test_agentsec1_public_outputs_exist_after_sample():
    from ai_objective_index.agentsec.manifest_scanner import build_agentsec1_sample_outputs

    build_agentsec1_sample_outputs()

    assert Path("public_launch/agentsec1/AGENTSEC1_SAMPLE_TOOL_MANIFEST.json").exists()
    assert Path("public_launch/agentsec1/AGENTSEC1_SCAN_RESULT.json").exists()
    assert Path("public_launch/agentsec1/AGENTSEC1_NEXT_STEPS.md").exists()
