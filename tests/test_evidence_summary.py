from ai_objective_index.models import ActionObject
from ai_objective_index.vnext.evidence_summary import build_evidence_summary


def test_evidence_summary_downgrades_no_source_objects():
    action_object = ActionObject(
        object_id="no-trace",
        name="No Trace Tool",
        object_type="ToolObject",
        summary="A candidate with no trace.",
        capabilities=["search"],
        categories=["tool"],
        confidence=0.9,
    )
    summary = build_evidence_summary(action_object, [])
    assert summary.evidence_status == "NO_TRACE"
    assert summary.confidence <= 0.2
    assert summary.source_trace_count == 0
