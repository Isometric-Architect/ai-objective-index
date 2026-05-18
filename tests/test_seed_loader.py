from ai_objective_index.seed_loader import (
    load_golden_queries,
    load_sample_index,
    load_source_traces,
)


def test_loads_sample_objects():
    objects = load_sample_index()

    assert len(objects) == 20
    assert objects[0].object_id == "aoi-pixelforge-api"


def test_loads_source_traces():
    traces = load_source_traces()

    assert len(traces) == 20
    assert traces[0].trace_id == "trace-pixelforge-pricing"


def test_loads_golden_queries():
    queries = load_golden_queries()

    assert len(queries) >= 20
    assert queries[0]["query_id"] == "golden-001"

