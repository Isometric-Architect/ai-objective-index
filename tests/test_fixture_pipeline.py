import json
from pathlib import Path

from ai_objective_index.extractor.fixture_pipeline import run_fixture_pipeline
from ai_objective_index.models import ActionObject
from ai_objective_index.scoring import score_object


def test_fixture_pipeline_writes_generated_json_files() -> None:
    result = run_fixture_pipeline()

    assert len(result["objects"]) >= 3
    assert len(result["traces"]) > 0
    for generated_file in result["generated_files"]:
        assert Path(generated_file).exists()

    json.dumps(result["objects"])
    action_object = ActionObject.model_validate(result["objects"][0])
    score = score_object(action_object)
    assert score.objective_score >= 0
