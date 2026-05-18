from ai_objective_index.compare import compare_objects
from ai_objective_index.seed_loader import load_sample_index, load_source_traces
from ai_objective_index.store import ObjectiveIndexStore


def test_compare_at_least_three_sample_objects():
    store = ObjectiveIndexStore(load_sample_index(), load_source_traces())

    result = compare_objects(
        store,
        [
            "aoi-pixelforge-api",
            "aoi-clearscan-ocr-api",
            "aoi-embedlite-api",
        ],
        query="cheap image generation API with commercial use terms",
        constraints={"max_monthly_budget_usd": 50},
    )

    assert len(result.comparison_table) == 3
    assert result.score_summary
    assert result.best_for

