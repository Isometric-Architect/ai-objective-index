from ai_objective_index.portfolio.pilot_feedback_form import package_pilot_feedback


def test_second_run_readout_includes_claim_boundary():
    result = package_pilot_feedback(sample=True)
    readout_path = result["artifact_paths"][7]
    text = __import__("pathlib").Path(readout_path).read_text(encoding="utf-8")
    assert "not external action authorization" in text.lower()
    assert "not certification" in text.lower()
