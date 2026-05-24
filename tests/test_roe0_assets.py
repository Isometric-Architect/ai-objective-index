from pathlib import Path


def test_roe0_docs_exist():
    docs = [
        "docs/roe_portfolio_strategy.md",
        "docs/roe_qbcpl_coding_governance.md",
        "docs/roe_public_private_split.md",
        "docs/agentsec_gate_plan.md",
        "docs/qira_code_releasegate_plan.md",
        "docs/datacapsule_engine_plan.md",
    ]

    for path in docs:
        assert Path(path).exists(), path


def test_roe0_outputs_exist():
    outputs = [
        "public_launch/roe0/ROE_PORTFOLIO_STRATEGY.json",
        "public_launch/roe0/ROE_SOURCE_INTAKE_AUDIT.json",
        "public_launch/roe0/ROE_TECHNICAL_PROTECTION_GATE.json",
        "public_launch/roe0/ROE0_SUMMARY.md",
    ]

    for path in outputs:
        assert Path(path).exists(), path


def test_roe0_docs_preserve_claim_boundaries():
    text = Path("docs/roe_portfolio_strategy.md").read_text(encoding="utf-8")

    assert "not verification" in text
    assert "security certification" in text
    assert "external action authorization" in text
