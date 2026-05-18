from ai_objective_index.models import ActionObject
from ai_objective_index.use_rights import UseRight, check_use_right, default_use_rights_for_object


def _object() -> ActionObject:
    return ActionObject(
        object_id="rights-object",
        name="Rights Object",
        object_type="APIObject",
        summary="Local test object for use-right checks.",
        status="EXTRACTED_UNVERIFIED",
        confidence=0.7,
    )


def test_read_rank_compare_quote_allowed() -> None:
    rights = default_use_rights_for_object(_object())
    assert rights["READ"]["decision"] == "ALLOW"
    assert rights["RANK"]["decision"] == "ALLOW"
    assert rights["COMPARE"]["decision"] == "ALLOW"
    assert rights["QUOTE"]["decision"] == "ALLOW"


def test_train_share_memory_action_not_allowed_by_default() -> None:
    action_object = _object()
    assert check_use_right(action_object, UseRight.TRAIN)["decision"] == "BLOCK"
    assert check_use_right(action_object, UseRight.SHARE)["decision"] == "BLOCK"
    assert check_use_right(action_object, UseRight.MEMORY)["decision"] == "HOLD"
    assert check_use_right(action_object, UseRight.ACTION)["decision"] == "BLOCK"
