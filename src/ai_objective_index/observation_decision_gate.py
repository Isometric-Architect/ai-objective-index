from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .public_metrics_snapshot import OBSERVATION_DIR


OUTPUT_BY_PHASE = {
    "0h": OBSERVATION_DIR / "OBSERVATION_DECISION_GATE_0H.json",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: str | Path) -> dict[str, Any]:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _snapshot_has_url_failure(snapshot: dict[str, Any]) -> bool:
    checks = snapshot.get("checks", {})
    public_urls = checks.get("public_urls", {})
    if isinstance(public_urls, dict) and public_urls.get("pass") is False:
        return True
    github = snapshot.get("github", {})
    hf = snapshot.get("huggingface", {})
    for payload in (github, hf):
        if isinstance(payload, dict) and payload.get("url_status") == "failed":
            return True
    return False


def run_observation_decision_gate(phase: str = "0h", write_result: bool = True) -> dict[str, Any]:
    if phase != "0h":
        raise ValueError("Package 8N currently supports the 0h decision gate.")

    snapshot = _read_json("public_ops/observation/OBSERVATION_SNAPSHOT_0H.json")
    baseline = _read_json("public_ops/PUBLIC_OPS_BASELINE_v0_1.json")
    issue_loop = _read_json("public_launch/PUBLIC_ISSUE_LOOP_RESULT.json")
    hygiene = _read_json("public_ops/WORKTREE_HYGIENE_AUDIT_v0_1.json")
    residual = _read_json("public_ops/residual_review/RESIDUAL_WORKTREE_REVIEW_v0_1.json")
    public_claim = _read_json("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json")
    launch_claim = _read_json("data/generated/launch_claim_guard_result_v0_2.json")

    reasons: list[str] = []
    if _snapshot_has_url_failure(snapshot):
        recommendation = "fix_public_url"
        reasons.append("Observation snapshot reports a public URL failure.")
    elif public_claim.get("overall_token") not in {None, "PASS"} or launch_claim.get("overall_token") not in {None, "PASS"}:
        recommendation = "fix_claims"
        reasons.append("A claim audit is not PASS.")
    elif residual.get("summary", {}).get("possible_sensitive", 0) or hygiene.get("classifications", {}).get("do_not_commit"):
        recommendation = "clean_worktree"
        reasons.append("Residual review or hygiene audit found sensitive/do-not-commit entries.")
    elif phase == "72h" and baseline.get("overall_token") == "PASS":
        recommendation = "prepare_release"
        reasons.append("72h stable observation can support a release draft if the user requests it.")
    else:
        recommendation = "observe_72h"
        reasons.append("Default recommendation: continue observing before community launch or release.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "phase": phase,
        "recommendation": recommendation,
        "reasons": reasons,
        "inputs": {
            "snapshot_available": bool(snapshot),
            "public_ops_baseline": baseline.get("overall_token", "missing"),
            "issue_loop_ready": issue_loop.get("feedback_loop_ready", False),
            "worktree_hygiene": hygiene.get("overall_token", "missing"),
            "residual_worktree_review": residual.get("overall_token", "missing"),
            "public_launch_claim_audit": public_claim.get("overall_token", "missing"),
            "launch_claim_guard": launch_claim.get("overall_token", "missing"),
        },
        "next_options": {
            "A": "continue observing",
            "B": "fix public URL issue",
            "C": "clean residual worktree",
            "D": "prepare GitHub Release later",
            "E": "prepare community post later",
        },
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "actual_publish_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_BY_PHASE[phase], result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AOI observation decision gate.")
    parser.add_argument("--phase", default="0h", choices=["0h"])
    args = parser.parse_args()
    result = run_observation_decision_gate(args.phase)
    print(f"observation_decision_gate: phase={result['phase']} recommendation={result['recommendation']}")


if __name__ == "__main__":
    main()
