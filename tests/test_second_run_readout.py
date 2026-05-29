from pathlib import Path

from ai_objective_index.portfolio.second_run_executor import REVIEWER_READOUT_PATH, run_second_run
from ai_objective_index.real_pypi_upload_gate import _repo_root


def test_second_run_readout_includes_claim_boundaries():
    run_second_run(sample=True, write_result=True)
    text = Path(_repo_root() / REVIEWER_READOUT_PATH).read_text(encoding="utf-8")
    assert "not an external pilot" in text.lower()
    assert "not an external pilot, security certification" in text.lower()
    assert "no github api calls" in text.lower()
