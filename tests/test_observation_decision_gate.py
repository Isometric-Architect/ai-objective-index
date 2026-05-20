import json
from pathlib import Path

from ai_objective_index.observation_decision_gate import run_observation_decision_gate


def _write(path: str, payload: dict):
    full = Path(path)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(json.dumps(payload), encoding="utf-8")


def test_observation_decision_gate_default_observe():
    _write("public_ops/observation/OBSERVATION_SNAPSHOT_0H.json", {"checks": {"public_urls": {"pass": True}}})
    _write("public_ops/PUBLIC_OPS_BASELINE_v0_1.json", {"overall_token": "PASS"})
    _write("public_launch/PUBLIC_ISSUE_LOOP_RESULT.json", {"feedback_loop_ready": True})
    _write("public_ops/WORKTREE_HYGIENE_AUDIT_v0_1.json", {"overall_token": "HOLD", "classifications": {"do_not_commit": []}})
    _write("public_ops/residual_review/RESIDUAL_WORKTREE_REVIEW_v0_1.json", {"overall_token": "HOLD_REVIEW", "summary": {"possible_sensitive": 0}})
    _write("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json", {"overall_token": "PASS"})
    _write("data/generated/launch_claim_guard_result_v0_2.json", {"overall_token": "PASS"})

    result = run_observation_decision_gate(write_result=False)

    assert result["recommendation"] == "observe_72h"


def test_observation_decision_gate_url_failure_and_sensitive_worktree():
    _write("public_ops/observation/OBSERVATION_SNAPSHOT_0H.json", {"checks": {"public_urls": {"pass": False}}})

    result = run_observation_decision_gate(write_result=False)

    assert result["recommendation"] == "fix_public_url"

    _write("public_ops/observation/OBSERVATION_SNAPSHOT_0H.json", {"checks": {"public_urls": {"pass": True}}})
    _write("public_ops/residual_review/RESIDUAL_WORKTREE_REVIEW_v0_1.json", {"overall_token": "BLOCK", "summary": {"possible_sensitive": 1}})
    _write("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json", {"overall_token": "PASS"})
    _write("data/generated/launch_claim_guard_result_v0_2.json", {"overall_token": "PASS"})

    result = run_observation_decision_gate(write_result=False)

    assert result["recommendation"] == "clean_worktree"
