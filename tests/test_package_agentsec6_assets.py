from pathlib import Path

from ai_objective_index.agentsec.package6 import run_agentsec6_package
from ai_objective_index.agentsec_claim_audit import run_agentsec_claim_audit


ROOT = Path(__file__).resolve().parents[1]


def test_agentsec6_docs_exist():
    assert (ROOT / "docs" / "agentsec6_manifest_corpus_ingestion.md").exists()


def test_agentsec6_outputs_exist_after_generation():
    run_agentsec6_package()
    run_agentsec_claim_audit(write_result=True)

    for relative in [
        "public_launch/agentsec6/AGENTSEC6_SAMPLE_MANIFEST_CORPUS.json",
        "public_launch/agentsec6/AGENTSEC6_CORPUS_INTAKE_RESULT.json",
        "public_launch/agentsec6/AGENTSEC6_POLICY_GATE_RESULT.json",
        "public_launch/agentsec6/AGENTSEC6_CORPUS_REPORT.md",
        "public_launch/agentsec6/AGENTSEC6_PACKAGE_RESULT.json",
        "public_launch/agentsec6/AGENTSEC6_NEXT_STEPS.md",
        "public_launch/agentsec6/AGENTSEC_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert (ROOT / relative).exists()


def test_agentsec6_docs_preserve_claim_boundary():
    text = (ROOT / "docs" / "agentsec6_manifest_corpus_ingestion.md").read_text(encoding="utf-8")

    assert "does not call live MCP servers" in text
    assert "certify security" in text
    assert "authorize external actions" in text
