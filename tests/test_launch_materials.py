from pathlib import Path


def test_issue_templates_exist():
    expected = [
        ".github/ISSUE_TEMPLATE/wrong_extracted_field.md",
        ".github/ISSUE_TEMPLATE/failed_query.md",
        ".github/ISSUE_TEMPLATE/add_new_tool.md",
        ".github/ISSUE_TEMPLATE/scoring_dispute.md",
    ]
    for path in expected:
        assert Path(path).exists()


def test_community_launch_doc_mentions_read_only():
    text = Path("docs/community_launch.md").read_text(encoding="utf-8").lower()

    assert "read-only" in text
    assert "please test and break" in text


def test_hf_dataset_card_and_jsonl_files():
    readme = Path("hf_dataset/README.md").read_text(encoding="utf-8").lower()
    assert "not a quality guarantee" in readme

    for path in [
        "hf_dataset/action_objects.jsonl",
        "hf_dataset/source_traces.jsonl",
        "hf_dataset/objective_scores.jsonl",
        "hf_dataset/golden_queries.jsonl",
    ]:
        lines = Path(path).read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 1

