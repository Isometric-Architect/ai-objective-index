from ai_objective_index.seed_loader import load_sample_index, load_source_traces
from ai_objective_index.source_trace import get_source_trace
from ai_objective_index.store import ObjectiveIndexStore


def test_get_traces_by_object_id():
    store = ObjectiveIndexStore(load_sample_index(), load_source_traces())

    traces = get_source_trace(store, "aoi-pixelforge-api")

    assert len(traces) == 1
    assert traces[0]["field"] == "pricing"


def test_filter_traces_by_field():
    store = ObjectiveIndexStore(load_sample_index(), load_source_traces())

    traces = get_source_trace(store, "aoi-pixelforge-api", field="pricing")
    misses = get_source_trace(store, "aoi-pixelforge-api", field="policies")

    assert len(traces) == 1
    assert misses == []

