from pathlib import Path


def test_agentsec2_docs_exist():
    assert Path("docs/agentsec2_policy_gate.md").exists()
    assert Path("docs/agentsec_policy_profiles.md").exists()


def test_agentsec2_public_outputs_exist_after_sample():
    from ai_objective_index.agentsec.policy_gate import build_agentsec2_sample_outputs

    build_agentsec2_sample_outputs()

    assert Path("public_launch/agentsec2/AGENTSEC2_SAMPLE_MANIFEST_SET.json").exists()
    assert Path("public_launch/agentsec2/AGENTSEC2_POLICY_PROFILE.json").exists()
    assert Path("public_launch/agentsec2/AGENTSEC2_NEXT_STEPS.md").exists()
