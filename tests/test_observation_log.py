from pathlib import Path

from ai_objective_index.observation_log import create_observation_assets


def test_observation_log_created():
    result = create_observation_assets()
    text = Path(result["observation_log_path"]).read_text(encoding="utf-8")

    assert "Hour 72 Check" in text
    assert "No immediate attention does not mean failure" in text

