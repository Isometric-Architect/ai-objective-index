from pathlib import Path


def test_package_9e_docs_and_schemas_exist():
    assert Path("docs/vnext/package_9e_probe_before_use_mvp.md").exists()
    assert Path("docs/vnext/probe_limitations.md").exists()
    assert Path("schemas/vnext/probe_plan.schema.json").exists()
    assert Path("schemas/vnext/probe_route_overlay.schema.json").exists()


def test_package_9e_public_outputs_created_by_demo():
    from ai_objective_index.vnext.probe_cli_demo import run_probe_cli_demo

    run_probe_cli_demo("image API", "select source-traced candidates", data_scope="sample", limit=1)
    assert Path("public_launch/wave7/PACKAGE_9E_PROBE_BEFORE_USE_RESULT.json").exists()
    assert Path("public_launch/wave7/PACKAGE_9E_NEXT_STEPS.md").exists()
