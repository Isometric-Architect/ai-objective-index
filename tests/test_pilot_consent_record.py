from ai_objective_index.portfolio.pilot_consent_record import build_consent_record, consent_record_to_jsonable


def test_consent_record_serializes():
    record = build_consent_record(
        intake_id="intake-1",
        consent_id="consent-1",
        consent_status="owner_provided",
        allowed_artifacts=["mcp_manifest"],
    )
    payload = consent_record_to_jsonable(record)
    assert payload["schema"] == "ResidualOps_PilotConsentRecord/v0.1"
    assert payload["consent_status"] == "owner_provided"
    assert "clone_repo" in payload["disallowed_actions"]
