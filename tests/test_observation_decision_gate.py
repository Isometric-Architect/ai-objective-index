from ai_objective_index import observation_decision_gate as gate_module


def _fake_reader(mapping: dict[str, dict]):
    def read(path: str):
        return mapping.get(str(path).replace("\\", "/"), {})

    return read


def test_observation_decision_gate_default_observe(monkeypatch):
    mapping = {
        "public_ops/observation/OBSERVATION_SNAPSHOT_0H.json": {"checks": {"public_urls": {"pass": True}}},
        "public_ops/PUBLIC_OPS_BASELINE_v0_1.json": {"overall_token": "PASS"},
        "public_launch/PUBLIC_ISSUE_LOOP_RESULT.json": {"feedback_loop_ready": True},
        "public_ops/WORKTREE_HYGIENE_AUDIT_v0_1.json": {"overall_token": "HOLD", "classifications": {"do_not_commit": []}},
        "public_ops/residual_review/RESIDUAL_WORKTREE_REVIEW_v0_1.json": {"overall_token": "HOLD_REVIEW", "summary": {"possible_sensitive": 0}},
        "public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json": {"overall_token": "PASS"},
        "data/generated/launch_claim_guard_result_v0_2.json": {"overall_token": "PASS"},
    }
    monkeypatch.setattr(gate_module, "_read_json", _fake_reader(mapping))

    result = gate_module.run_observation_decision_gate(write_result=False)

    assert result["recommendation"] == "observe_72h"


def test_observation_decision_gate_url_failure_and_sensitive_worktree(monkeypatch):
    mapping = {
        "public_ops/observation/OBSERVATION_SNAPSHOT_0H.json": {"checks": {"public_urls": {"pass": False}}},
    }
    monkeypatch.setattr(gate_module, "_read_json", _fake_reader(mapping))

    result = gate_module.run_observation_decision_gate(write_result=False)

    assert result["recommendation"] == "fix_public_url"

    mapping = {
        "public_ops/observation/OBSERVATION_SNAPSHOT_0H.json": {"checks": {"public_urls": {"pass": True}}},
        "public_ops/residual_review/RESIDUAL_WORKTREE_REVIEW_v0_1.json": {"overall_token": "BLOCK", "summary": {"possible_sensitive": 1}},
        "public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json": {"overall_token": "PASS"},
        "data/generated/launch_claim_guard_result_v0_2.json": {"overall_token": "PASS"},
    }
    monkeypatch.setattr(gate_module, "_read_json", _fake_reader(mapping))

    result = gate_module.run_observation_decision_gate(write_result=False)

    assert result["recommendation"] == "clean_worktree"
