from ai_objective_index.integrated_store import get_store_for_scope
from ai_objective_index.scoring import score_object


def test_integrated_store_scope_counts() -> None:
    sample = get_store_for_scope("sample")
    generated = get_store_for_scope("generated")
    integrated = get_store_for_scope("integrated")

    sample_count = len(sample.list_objects())
    generated_count = len(generated.list_objects())
    integrated_count = len(integrated.list_objects())

    assert sample_count > 0
    assert generated_count >= 3
    assert integrated_count >= sample_count + generated_count


def test_generated_objects_can_be_scored() -> None:
    store = get_store_for_scope("generated")
    action_object = store.list_objects()[0]

    score = score_object(action_object, traces=store.get_traces(action_object.object_id))

    assert score.objective_score >= 0
    assert score.status == "EXTRACTED_UNVERIFIED"

