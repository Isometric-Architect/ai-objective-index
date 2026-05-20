import json
from pathlib import Path

from ai_objective_index.vnext_capability_trust_audit import run_capability_trust_claim_audit


def test_package_9b_docs_and_schemas_exist():
    required = [
        "docs/vnext/package_9b_capability_trust_schema_mvp.md",
        "docs/vnext/capability_trust_card.md",
        "docs/vnext/capability_route_decision.md",
        "docs/vnext/capability_risk_boundary.md",
        "docs/vnext/capability_evidence_summary.md",
        "docs/vnext/capability_trust_profile.md",
        "docs/vnext/capability_trust_limitations.md",
        "schemas/vnext/capability_trust_card.schema.json",
        "schemas/vnext/capability_route_decision.schema.json",
        "schemas/vnext/capability_risk_boundary.schema.json",
        "schemas/vnext/capability_evidence_summary.schema.json",
        "schemas/vnext/capability_trust_report.schema.json",
    ]
    for path in required:
        assert Path(path).exists(), path


def test_capability_trust_claim_audit_passes_and_records_boundaries():
    result = run_capability_trust_claim_audit()
    assert result["overall_token"] == "PASS"
    assert result["pypi_upload_performed"] is False
    assert result["mcp_registry_submission_performed"] is False
    payload = json.loads(Path("public_launch/wave4/CAPABILITY_TRUST_CLAIM_BOUNDARY_AUDIT.json").read_text())
    assert payload["token_printed"] is False
