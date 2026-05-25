from ai_objective_index.agentsec.fixture_corpus import build_fixture_corpus, write_fixture_corpus


def test_agentsec5_fixture_corpus_is_public_safe():
    corpus = build_fixture_corpus()

    assert corpus["decision"] == "PASS_AGENTSEC5_FIXTURE_CORPUS_READY"
    assert corpus["fixture_count"] >= 6
    assert corpus["public_safe"] is True
    assert corpus["contains_private_kernel"] is False
    assert corpus["contains_private_negative_control_seeds"] is False
    assert corpus["network_used"] is False


def test_agentsec5_fixture_corpus_has_expected_decision_mix():
    corpus = build_fixture_corpus()
    decisions = {item["expected_decision"] for item in corpus["fixtures"]}

    assert "ALLOW_METADATA_ONLY" in decisions
    assert "HOLD_REVIEW_REQUIRED" in decisions
    assert "BLOCK_FORBIDDEN_ACTION" in decisions
    assert "BLOCK_UNSUPPORTED_CLAIM" in decisions


def test_agentsec5_fixture_corpus_writes_outputs():
    corpus = write_fixture_corpus()

    assert corpus["fixture_count"] >= 6
