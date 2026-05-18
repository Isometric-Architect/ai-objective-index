from ai_objective_index.report_metrics import (
    compute_missing_field_stats,
    compute_score_distribution,
    compute_source_trace_coverage,
    compute_status_counts,
)
from ai_objective_index.scoring import score_object
from ai_objective_index.seed_loader import load_sample_index, load_source_traces


def test_source_trace_coverage_returns_fraction():
    objects = load_sample_index()
    traces = load_source_traces()

    coverage = compute_source_trace_coverage(objects, traces)

    assert 0 <= coverage <= 1


def test_status_counts_returns_dict():
    counts = compute_status_counts(load_sample_index())

    assert isinstance(counts, dict)
    assert counts


def test_missing_field_stats_returns_summary():
    stats = compute_missing_field_stats(load_sample_index())

    assert isinstance(stats, dict)
    assert "by_field" in stats
    assert "objects_with_missing_fields" in stats


def test_score_distribution_works():
    objects = load_sample_index()[:3]
    traces = load_source_traces()
    trace_map = {}
    for trace in traces:
        trace_map.setdefault(trace.object_id, []).append(trace)
    scores = [
        score_object(action_object, traces=trace_map.get(action_object.object_id, []))
        for action_object in objects
    ]

    distribution = compute_score_distribution(scores)

    assert distribution["count"] == 3
    assert distribution["average"] is not None
    assert set(distribution["buckets"]) == {"0-24", "25-49", "50-74", "75-100"}

