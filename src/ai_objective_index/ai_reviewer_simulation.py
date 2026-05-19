from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import build_integrated_traces, get_store_for_scope
from .public_launch_claim_audit import run_public_launch_claim_audit


OUTPUT_DIR = Path("public_launch")
OUTPUT_PATH = OUTPUT_DIR / "AI_REVIEWER_SIMULATION_RESULT.json"

REVIEWER_ROLES = [
    "skeptic_reviewer",
    "developer_reviewer",
    "agent_user_reviewer",
    "data_quality_reviewer",
    "business_positioning_reviewer",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _read_text(path: str | Path) -> str:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


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


def _exists(path: str | Path) -> bool:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    return full.exists()


def _token(condition: bool, block: bool = False) -> str:
    if block:
        return "BLOCK"
    return "PASS" if condition else "HOLD"


def _public_beta_mcp_count() -> int:
    return len(get_store_for_scope("public_beta_mcp").list_objects())


def _source_trace_count() -> int:
    registry_traces = _repo_root() / "data" / "registry" / "mcp_registry_source_traces_v0_1.jsonl"
    if registry_traces.exists():
        return sum(1 for line in registry_traces.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip())
    return len(build_integrated_traces(include_sample=False, include_generated=False, include_mcp_registry=True, public_beta_mcp_only=True))


def _review(
    role: str,
    token: str,
    findings: list[str],
    required_fixes: list[str],
    evidence_files_checked: list[str],
    confidence: float,
) -> dict[str, Any]:
    return {
        "role": role,
        "token": token,
        "findings": findings,
        "required_fixes": required_fixes,
        "confidence": confidence,
        "evidence_files_checked": evidence_files_checked,
    }


def _skeptic_reviewer() -> dict[str, Any]:
    claim_audit = run_public_launch_claim_audit(write_result=False)
    readme = _read_text("README.md").lower()
    public_beta_verified = "public_beta_mcp is verified" in readme or "public_beta_mcp contains verified" in readme
    risky_count = int(claim_audit.get("risky_phrase_count", 0) or 0)
    token = _token(risky_count == 0 and not public_beta_verified, block=public_beta_verified)
    findings = [
        f"public launch risky phrase count: {risky_count}",
        "README does not describe public_beta_mcp as verified." if not public_beta_verified else "README may describe public_beta_mcp as verified.",
    ]
    fixes = []
    if risky_count:
        fixes.append("Rewrite public-facing launch claims using not verified, not security certified, and not quality guarantee language.")
    if public_beta_verified:
        fixes.append("Remove any wording that public_beta_mcp is verified.")
    return _review(
        "skeptic_reviewer",
        token,
        findings,
        fixes,
        [
            "README.md",
            "docs/community_launch.md",
            "docs/public_beta_release_plan.md",
            "public_launch/*.md",
            "release/public_beta_v0_2/*.md",
        ],
        0.9,
    )


def _developer_reviewer() -> dict[str, Any]:
    readme = _read_text("README.md").lower()
    smoke = _read_json("data/generated/smoke_all_result_v0_1.json")
    has_instructions = "python -m ai_objective_index" in readme and "package" in readme
    smoke_ok_or_documented = smoke.get("pass") is True or "python -m ai_objective_index.smoke_all" in readme
    token = _token(_exists("README.md") and has_instructions and smoke_ok_or_documented)
    fixes = []
    if not has_instructions:
        fixes.append("Add README commands for local install/demo/smoke checks.")
    if not smoke_ok_or_documented:
        fixes.append("Run smoke_all or document the smoke_all command.")
    return _review(
        "developer_reviewer",
        token,
        [
            f"README exists: {_exists('README.md')}",
            f"installation/demo commands documented: {has_instructions}",
            f"smoke_all passed or documented: {smoke_ok_or_documented}",
        ],
        fixes,
        ["README.md", "data/generated/smoke_all_result_v0_1.json"],
        0.86,
    )


def _agent_user_reviewer() -> dict[str, Any]:
    docs_blob = (
        _read_text("docs/mcp_usage.md")
        + "\n"
        + _read_text("docs/api_reference.md")
        + "\n"
        + _read_text("docs/huggingface_demo.md")
        + "\n"
        + _read_text("README.md")
    ).lower()
    checks = {
        "mcp_manifest": _exists("data/generated_mcp_tools_manifest.json"),
        "openapi": _exists("api/openapi.json"),
        "hf_space_link": HF_SPACE_URL.lower() in docs_blob,
        "source_trace_visible": "source trace" in docs_blob or _source_trace_count() > 0,
    }
    token = _token(all(checks.values()))
    fixes = [f"Resolve missing agent-user surface: {name}" for name, ok in checks.items() if not ok]
    return _review(
        "agent_user_reviewer",
        token,
        [f"{name}: {ok}" for name, ok in checks.items()],
        fixes,
        [
            "data/generated_mcp_tools_manifest.json",
            "api/openapi.json",
            "docs/mcp_usage.md",
            "docs/api_reference.md",
            "docs/huggingface_demo.md",
        ],
        0.88,
    )


def _data_quality_reviewer() -> dict[str, Any]:
    payload_audit = _read_json("data/registry/registry_payload_audit_v0_1.json")
    public_beta_count = int(payload_audit.get("public_beta_mcp_count") or _public_beta_mcp_count())
    source_trace_count = int(payload_audit.get("trace_count") or _source_trace_count())
    fixture_leak = payload_audit.get("fixture_leak_detected")
    raw_payload_mode = payload_audit.get("raw_payload_mode")
    checks = {
        "public_beta_mcp_count_gt_zero": public_beta_count > 0,
        "source_trace_count_gt_zero": source_trace_count > 0,
        "fixture_leak_false": fixture_leak is False,
        "manual_or_live_raw": raw_payload_mode in {"manual_raw", "live_raw"},
    }
    token = _token(all(checks.values()))
    fixes = []
    if not checks["public_beta_mcp_count_gt_zero"]:
        fixes.append("Reprocess real/manual MCP registry raw payload so public_beta_mcp has candidates.")
    if not checks["source_trace_count_gt_zero"]:
        fixes.append("Rebuild registry source traces.")
    if fixture_leak is not False:
        fixes.append("Run registry_payload_audit and remove fixture leakage before public beta.")
    if not checks["manual_or_live_raw"]:
        fixes.append("Activate manual_raw or live_raw registry payload before public beta.")
    return _review(
        "data_quality_reviewer",
        token,
        [
            f"public_beta_mcp_count: {public_beta_count}",
            f"source_trace_count: {source_trace_count}",
            f"fixture_leak_detected: {fixture_leak}",
            f"raw_payload_mode: {raw_payload_mode}",
        ],
        fixes,
        ["data/registry/registry_payload_audit_v0_1.json", "data/registry/mcp_registry_beta_candidates_v0_1.jsonl"],
        0.9,
    )


def _business_positioning_reviewer() -> dict[str, Any]:
    readme = _read_text("README.md").lower()
    community = _read_text("docs/community_launch.md").lower()
    one_line = "read-only mcp/api" in readme or "read-only objective ranking" in readme
    target_users = all(token in community for token in ["mcp", "developer", "hugging face"])
    claim_audit = run_public_launch_claim_audit(write_result=False)
    no_overclaim = int(claim_audit.get("risky_phrase_count", 0) or 0) == 0
    token = _token(one_line and target_users and no_overclaim)
    fixes = []
    if not one_line:
        fixes.append("Add a concise one-line read-only MCP/API positioning statement.")
    if not target_users:
        fixes.append("Identify target users in community launch docs.")
    if not no_overclaim:
        fixes.append("Remove public overclaim wording from launch materials.")
    return _review(
        "business_positioning_reviewer",
        token,
        [
            f"one-line positioning exists: {one_line}",
            f"target users identified: {target_users}",
            f"no overclaim findings: {no_overclaim}",
            f"GitHub: {GITHUB_URL}",
            f"HF Space: {HF_SPACE_URL}",
            f"HF Dataset: {HF_DATASET_URL}",
        ],
        fixes,
        ["README.md", "docs/community_launch.md", "public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json"],
        0.84,
    )


def run_ai_reviewer_simulation(write_result: bool = True) -> dict[str, Any]:
    reviewers = [
        _skeptic_reviewer(),
        _developer_reviewer(),
        _agent_user_reviewer(),
        _data_quality_reviewer(),
        _business_positioning_reviewer(),
    ]
    if any(item["token"] == "BLOCK" for item in reviewers):
        overall = "BLOCK"
    elif all(item["token"] == "PASS" for item in reviewers):
        overall = "PASS"
    else:
        overall = "HOLD"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "reviewer_count": len(reviewers),
        "reviewers": {item["role"]: item for item in reviewers},
        "external_llm_used": False,
        "live_network_used": False,
        "private_reviewer_required": False,
        "public_switch_performed": False,
        "community_post_performed": False,
        "next_action": "Run no_contact_launch_gate and decide whether to keep private or public-switch manually."
        if overall != "BLOCK"
        else "Resolve BLOCK findings before any public launch decision.",
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_ai_reviewer_simulation()
    print(
        "ai_reviewer_simulation: "
        f"{result['overall_token']} "
        f"reviewers={result['reviewer_count']} "
        "external_llm_used=False"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
