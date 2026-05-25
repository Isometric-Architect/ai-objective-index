from ai_objective_index.datacapsule.fixture_corpus import build_fixture_corpus, write_fixture_corpus


def test_datacapsule5_fixture_corpus_is_public_safe():
    corpus = build_fixture_corpus()

    assert corpus["decision"] == "PASS_DATACAPSULE5_FIXTURE_CORPUS_READY"
    assert corpus["fixture_count"] >= 8
    assert corpus["public_safe"] is True
    assert corpus["contains_private_kernel"] is False
    assert corpus["contains_real_private_data"] is False
    assert corpus["network_used"] is False


def test_datacapsule5_fixture_corpus_has_expected_decision_mix():
    corpus = build_fixture_corpus()
    decisions = {item["expected_decision"] for item in corpus["fixtures"]}

    assert "ALLOW_USE" in decisions
    assert "HOLD_SOURCE_RIGHTS_REVIEW" in decisions
    assert "HOLD_PROMPT_INJECTION_REVIEW" in decisions
    assert "BLOCK_LICENSE_RESTRICTED" in decisions
    assert "BLOCK_UNSUPPORTED_CLAIM" in decisions
    assert "BLOCK_ACTION_USE" in decisions


def test_datacapsule5_fixture_corpus_writes_outputs():
    corpus = write_fixture_corpus()

    assert corpus["fixture_count"] >= 8
