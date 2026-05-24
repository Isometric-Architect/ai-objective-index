from ai_objective_index.datacapsule.eval_leak import build_eval_leak_separation_report


def test_eval_leak_passes_when_paths_are_separated():
    report = build_eval_leak_separation_report(
        {
            "files": [
                {"path": "docs/train.md", "purpose": ["train"]},
                {"path": "docs/eval.md", "purpose": ["evaluate"]},
            ]
        }
    )

    assert report.decision == "PASS_EVAL_SEPARATION_LOCAL_METADATA"
    assert report.overlap_count == 0
    assert report.can_prove_eval_cleanliness is False


def test_eval_leak_blocks_direct_train_eval_overlap():
    report = build_eval_leak_separation_report(
        {
            "files": [
                {"path": "docs/shared.md", "purpose": ["train", "evaluate"]},
            ]
        }
    )

    assert report.decision == "BLOCK_EVAL_LEAK_CONFLICT"
    assert report.overlap_paths == ["docs/shared.md"]


def test_eval_leak_holds_missing_purpose_or_flag():
    report = build_eval_leak_separation_report(
        {
            "files": [
                {"path": "docs/unknown.md"},
                {"path": "docs/eval.md", "purpose": ["evaluate"], "risk_flags": {"eval_leak": True}},
            ]
        }
    )

    assert report.decision == "HOLD_EVAL_LEAK_REVIEW"
    assert report.network_used is False
