from pathlib import Path

from ai_objective_index.public_observation_plan import create_public_observation_assets


def test_public_observation_plan_mentions_early_signal_boundary():
    result = create_public_observation_assets()
    path = Path(result["observation_plan_path"])
    text = path.read_text(encoding="utf-8")

    assert path.exists()
    assert "First 72 Hours" in text
    assert "No immediate attention does not mean failure" in text

