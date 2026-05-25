from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_agentsec5_docs_exist():
    for relative in [
        "docs/agentsec5_manifest_fixture_corpus.md",
        "docs/agentsec_negative_controls.md",
    ]:
        assert (ROOT / relative).exists()


def test_agentsec5_outputs_exist_after_generation():
    for relative in [
        "public_launch/agentsec5/AGENTSEC5_FIXTURE_CORPUS.json",
        "public_launch/agentsec5/AGENTSEC5_FIXTURE_CORPUS_REPORT.md",
        "public_launch/agentsec5/AGENTSEC5_NEGATIVE_CONTROL_RESULT.json",
        "public_launch/agentsec5/AGENTSEC5_NEGATIVE_CONTROL_REPORT.md",
        "public_launch/agentsec5/AGENTSEC5_PACKAGE_RESULT.json",
        "public_launch/agentsec5/AGENTSEC5_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists()


def test_agentsec5_docs_preserve_claim_boundary():
    text = (ROOT / "docs" / "agentsec_negative_controls.md").read_text(encoding="utf-8")

    assert "not verification" in text
    assert "security certification" in text
    assert "action authorization" in text
