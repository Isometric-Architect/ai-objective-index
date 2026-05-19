import json
from pathlib import Path

from ai_objective_index.release_next_decision_gate import run_release_next_decision_gate


def _write(path: str, payload: dict):
    full = Path(path)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(json.dumps(payload), encoding="utf-8")


def test_release_next_decision_gate_default_observe():
    _write("public_ops/PUBLIC_OPS_BASELINE_v0_1.json", {"overall_token": "PASS"})
    _write("public_ops/WORKTREE_HYGIENE_AUDIT_v0_1.json", {"overall_token": "HOLD"})
    _write("public_launch/PUBLIC_URL_QA_RESULT.json", {"overall_token": "PASS"})
    _write("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json", {"overall_token": "PASS"})
    _write("data/generated/launch_claim_guard_result_v0_2.json", {"overall_token": "PASS"})

    result = run_release_next_decision_gate(write_result=False)

    assert result["recommendation"] == "observe_72h"


def test_release_next_decision_gate_blocks_claim_or_hygiene():
    _write("public_ops/WORKTREE_HYGIENE_AUDIT_v0_1.json", {"overall_token": "BLOCK"})
    _write("public_launch/PUBLIC_URL_QA_RESULT.json", {"overall_token": "PASS"})
    _write("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json", {"overall_token": "PASS"})
    _write("data/generated/launch_claim_guard_result_v0_2.json", {"overall_token": "PASS"})

    result = run_release_next_decision_gate(write_result=False)

    assert result["recommendation"] == "clean_repo"
