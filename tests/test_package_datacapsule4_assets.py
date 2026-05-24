from pathlib import Path


def test_datacapsule4_docs_and_actions_exist():
    for path in [
        "docs/datacapsule4_ci_artifact_bridge.md",
        "docs/datacapsule_ci_bridge_limitations.md",
        ".github/actions/datacapsule-corpus-manifest-artifact/action.yml",
        "examples/datacapsule_corpus_manifest_artifact_workflow.yml",
    ]:
        assert Path(path).exists(), path


def test_datacapsule4_outputs_exist_after_sample():
    from ai_objective_index.datacapsule.ci_artifact_bridge import audit_datacapsule4_action_manifest, run_sample
    from ai_objective_index.datacapsule_claim_audit import run_datacapsule_claim_audit

    run_sample()
    audit_datacapsule4_action_manifest()
    run_datacapsule_claim_audit()

    for path in [
        "public_launch/datacapsule4/DATACAPSULE4_SAMPLE_MANIFEST.csv",
        "public_launch/datacapsule4/DATACAPSULE4_NORMALIZED_MANIFEST.json",
        "public_launch/datacapsule4/DATACAPSULE4_CORPUS_CAPSULE.json",
        "public_launch/datacapsule4/DATACAPSULE4_CORPUS_RESULT.json",
        "public_launch/datacapsule4/DATACAPSULE4_EVAL_LEAK_SEPARATION_REPORT.json",
        "public_launch/datacapsule4/DATACAPSULE4_INTAKE_RESULT.json",
        "public_launch/datacapsule4/DATACAPSULE4_BRIDGE_RESULT.json",
        "public_launch/datacapsule4/DATACAPSULE4_BRIDGE_REPORT.md",
        "public_launch/datacapsule4/DATACAPSULE4_ACTION_MANIFEST_AUDIT.json",
        "public_launch/datacapsule4/DATACAPSULE4_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/datacapsule4/DATACAPSULE4_NEXT_STEPS.md",
    ]:
        assert Path(path).exists(), path


def test_datacapsule4_does_not_auto_enable_workflow():
    assert not Path(".github/workflows/datacapsule-corpus-manifest-artifact.yml").exists()


def test_datacapsule4_docs_preserve_no_api_or_token_boundary():
    text = Path("docs/datacapsule4_ci_artifact_bridge.md").read_text(encoding="utf-8")

    assert "does not crawl directories" in text
    assert "call GitHub APIs" in text
    assert "handle tokens" in text
