from ai_objective_index.datacapsule.models import DataCapsule, DataUseBoundary, DataUsePermission, RiskFlags


def test_datacapsule_model_serializes():
    permissions = DataUsePermission(
        train=DataUseBoundary(use_class="train", decision="HOLD_SOURCE_RIGHTS_REVIEW"),
        retrieve=DataUseBoundary(use_class="retrieve", decision="ALLOW_USE", allowed=True),
        evaluate=DataUseBoundary(use_class="evaluate", decision="ALLOW_USE", allowed=True),
        summarize=DataUseBoundary(use_class="summarize", decision="ALLOW_USE", allowed=True),
        share=DataUseBoundary(use_class="share", decision="HOLD_SOURCE_RIGHTS_REVIEW"),
        act=DataUseBoundary(use_class="act", decision="BLOCK_ACTION_USE"),
    )
    capsule = DataCapsule(
        capsule_id="datacapsule-test",
        data_id="fixture.local/data",
        name="Fixture Data",
        raw_hash="abc123",
        use_permissions=permissions,
        risk_flags=RiskFlags(),
    )

    payload = capsule.model_dump(mode="json", by_alias=True)

    assert payload["schema"] == "DataCapsule/v0.1"
    assert payload["use_permissions"]["act"]["decision"] == "BLOCK_ACTION_USE"
    assert payload["can_authorize_action"] is False
