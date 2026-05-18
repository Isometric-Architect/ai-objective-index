from pathlib import Path

from ai_objective_index.launch_claim_guard import run_launch_claim_guard, save_launch_claim_guard


def test_launch_claim_guard_detects_positive_risky_claim():
    test_dir = Path("data/generated/test_launch_claim_guard")
    test_dir.mkdir(parents=True, exist_ok=True)
    bad = test_dir / "bad.md"
    bad.write_text("AOI provides verified MCP servers and security certified rankings.\n", encoding="utf-8")

    result = run_launch_claim_guard([bad])

    assert result["overall_token"] == "HOLD"
    assert result["risky_phrase_count"] >= 1


def test_launch_claim_guard_allows_forbidden_context():
    test_dir = Path("data/generated/test_launch_claim_guard")
    test_dir.mkdir(parents=True, exist_ok=True)
    ok = test_dir / "ok.md"
    ok.write_text("Forbidden claims:\n- AOI is not security certified.\n", encoding="utf-8")

    result = run_launch_claim_guard([ok])
    path = save_launch_claim_guard(result)

    assert path.exists()
    assert result["overall_token"] == "PASS"
    assert result["risky_phrase_count"] == 0
