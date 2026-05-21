from pathlib import Path


def test_package_9f_docs_and_outputs_exist():
    from ai_objective_index.vnext_distribution_gate import run_vnext_distribution_gate
    from ai_objective_index.vnext_pypi_resume_gate import run_vnext_pypi_resume_gate

    run_vnext_distribution_gate(write_result=True)
    run_vnext_pypi_resume_gate(write_result=True)
    assert Path("docs/vnext/package_9f_vnext_distribution_gate.md").exists()
    assert Path("docs/vnext/residualops_alignment.md").exists()
    assert Path("public_launch/wave8/VNEXT_DISTRIBUTION_GATE_RESULT.json").exists()
    assert Path("public_launch/wave8/NEXT_8Q_A_RESUME_INSTRUCTIONS.md").exists()
