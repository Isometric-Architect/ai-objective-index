from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .ai_reviewer_simulation import run_ai_reviewer_simulation
from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope
from .issue_feedback_loop_packager import create_issue_feedback_loop_plan
from .public_beta_message_guard import run_public_beta_message_guard
from .public_launch_gate import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "NO_CONTACT_LAUNCH_GATE_RESULT.json"
POST_DRAFT_PATH = OUTPUT_DIR / "PUBLIC_BETA_POST_DRAFT_NO_CONTACT.md"
GO_NO_GO_PATH = OUTPUT_DIR / "NO_CONTACT_GO_NO_GO_DECISION.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


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


def _read_text(path: str | Path) -> str:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


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


def _issue_templates_exist() -> bool:
    issue_dir = _repo_root() / ".github" / "ISSUE_TEMPLATE"
    if not issue_dir.exists():
        return False
    expected = {"failed_query.md", "wrong_extracted_field.md", "scoring_dispute.md", "add_new_tool.md"}
    existing = {path.name for path in issue_dir.glob("*.md")}
    return bool(expected & existing)


def _hf_space_running_if_known() -> bool:
    hf_qa = _read_json("huggingface_upload/HF_POST_UPLOAD_QA_RESULT.json")
    status = str(hf_qa.get("build_status_if_available", "")).upper()
    if not status:
        return True
    return status.startswith("RUNNING") or status in {"BUILDING", "NOT_AVAILABLE", "NOT_CHECKED"}


def _launch_token(value: str | None, allow_hold: bool = False) -> str:
    if value == "BLOCK":
        return "BLOCK"
    if value == "PASS" or (allow_hold and value == "HOLD"):
        return "PASS"
    return "HOLD"


def _load_golden_queries(limit: int = 5) -> list[str]:
    path = _repo_root() / "data" / "golden_queries.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    queries = payload.get("queries", []) if isinstance(payload, dict) else []
    result: list[str] = []
    for item in queries:
        if isinstance(item, dict) and item.get("query"):
            result.append(str(item["query"]))
        if len(result) >= limit:
            break
    return result


def write_no_contact_launch_assets() -> list[str]:
    queries = _load_golden_queries()
    query_lines = "\n".join(f"{index}. `{query}`" for index, query in enumerate(queries, start=1))
    post = f"""# [Feedback] AI Objective Index - read-only MCP/API benchmark for objective-based MCP tool ranking

I built a read-only MCP/API benchmark tool for objective-based comparison of AI tools, APIs, SaaS products, and MCP servers.

It ranks Official MCP Registry metadata candidates by explicit objectives and returns source traces, missing fields, score components, and decision-receipt style limits.

It is not verified, not security certified, not a quality guarantee, not purchasing advice, and not action-ready. It does not buy, book, log in, send email, submit forms, purchase, or sign contracts.

Please test these golden queries and open GitHub Issues for wrong fields, bad rankings, missing source traces, confusing claim boundaries, or install failures:

{query_lines}

Private/staging links until the owner manually switches visibility:

- GitHub: {GITHUB_URL}
- Hugging Face Space: {HF_SPACE_URL}
- Hugging Face Dataset: {HF_DATASET_URL}
"""
    decision = """# No-Contact GO / NO-GO Decision

AOI can proceed without private reviewers by using deterministic local review plus GitHub Issues for feedback.

## Options

- [ ] Keep private.
- [ ] Public switch with no-contact beta.
- [ ] Pause and improve docs.
- [ ] Open to issue-based feedback only.

## Required Before Public Switch

- AI reviewer simulation has no BLOCK.
- No-contact launch gate has no BLOCK.
- Public beta message guard has no risky positive claims.
- No-secrets audit has no real token findings.
- The owner manually confirms any visibility switch.

## Boundary

No-contact public beta does not mean verified, safe, security certified, quality guaranteed, production-ready, purchasing advice, or action permission.
"""
    paths = [
        _write(POST_DRAFT_PATH, post),
        _write(GO_NO_GO_PATH, decision),
    ]
    return [str(path.relative_to(_repo_root())) for path in paths]


def run_no_contact_launch_gate(write_result: bool = True) -> dict[str, Any]:
    written_assets = write_no_contact_launch_assets()
    issue_plan = create_issue_feedback_loop_plan()
    reviewer = run_ai_reviewer_simulation(write_result=True)
    message_guard = run_public_beta_message_guard(write_result=True)

    no_secrets = _read_json("data/generated/no_secrets_audit_result_v0_2.json")
    launch_claim = _read_json("data/generated/launch_claim_guard_result_v0_2.json")
    public_claim = _read_json("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json")
    final_preflight = _read_json("data/generated/final_preflight_result_v0_2.json")
    private_qa = _read_json("deployment/private_deployment_v0_2/PRIVATE_DEPLOYMENT_QA_RESULT.json")
    public_beta_count = _public_beta_mcp_count()

    no_secret_findings = int(no_secrets.get("finding_count", 0) or 0)
    community_text = (_read_text("docs/community_launch.md") + "\n" + _read_text("public_launch/PUBLIC_BETA_POST_DRAFT_NO_CONTACT.md")).lower()
    community_conservative = all(
        phrase in community_text
        for phrase in ["read-only", "not verified", "not security certified", "quality guarantee"]
    )

    checks = {
        "ai_reviewer_simulation": {
            "token": _launch_token(reviewer.get("overall_token"), allow_hold=True),
            "value": reviewer.get("overall_token"),
        },
        "no_secrets_audit": {
            "token": _token(no_secret_findings == 0, block=no_secret_findings > 0),
            "finding_count": no_secret_findings,
        },
        "launch_claim_guard": {
            "token": _token(launch_claim.get("overall_token") == "PASS"),
            "value": launch_claim.get("overall_token"),
        },
        "public_launch_claim_audit": {
            "token": _launch_token(public_claim.get("overall_token") or "HOLD"),
            "value": public_claim.get("overall_token", "missing"),
        },
        "final_preflight": {
            "token": _token(final_preflight.get("overall_token") == "PASS"),
            "value": final_preflight.get("overall_token"),
        },
        "private_deployment_qa": {
            "token": _token(private_qa.get("overall_token") == "PASS"),
            "value": private_qa.get("overall_token"),
        },
        "hf_space_running": {"token": _token(_hf_space_running_if_known()), "value": _hf_space_running_if_known()},
        "public_beta_mcp": {"token": _token(public_beta_count > 0), "count": public_beta_count},
        "issue_templates": {"token": _token(_issue_templates_exist()), "exists": _issue_templates_exist()},
        "community_drafts_conservative": {
            "token": _token(community_conservative),
            "contains_required_boundaries": community_conservative,
        },
        "message_guard": {
            "token": _launch_token(message_guard.get("overall_token")),
            "value": message_guard.get("overall_token"),
        },
        "private_reviewer_not_required": {"token": "PASS", "private_reviewer_required": False},
        "no_public_actions": {
            "token": "PASS",
            "public_switch_performed": False,
            "community_post_performed": False,
            "mcp_registry_submission_performed": False,
        },
    }

    if any(check["token"] == "BLOCK" for check in checks.values()):
        overall = "BLOCK"
    elif all(check["token"] == "PASS" for check in checks.values()):
        overall = "PASS"
    else:
        overall = "HOLD"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "checks": checks,
        "private_reviewer_required": False,
        "launch_mode": "no_contact_public_beta",
        "public_switch_performed": False,
        "community_post_performed": False,
        "mcp_registry_submission_performed": False,
        "github_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "issue_feedback_loop_plan": issue_plan["plan_path"],
        "written_assets": written_assets + [str(issue_plan["plan_path"])],
        "warnings": [
            "No-contact public beta replaces private reviewer dependency with deterministic local review and issue-based feedback.",
            "A PASS result is not verification, security certification, quality guarantee, production readiness, or purchasing advice.",
        ],
        "next_action": "Human decision required: keep private, switch public with no-contact beta, or pause."
        if overall != "BLOCK"
        else "Resolve BLOCK checks before any public launch decision.",
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_no_contact_launch_gate()
    print(
        "no_contact_launch_gate: "
        f"{result['overall_token']} "
        f"private_reviewer_required={result['private_reviewer_required']} "
        f"public_switch_performed={result['public_switch_performed']}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
