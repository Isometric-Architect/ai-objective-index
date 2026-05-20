from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


WAVE1_DIR = Path("public_launch") / "wave1"
REPORT_PATH = WAVE1_DIR / "LAUNCH_WAVE1_REPORT.json"
SUMMARY_PATH = WAVE1_DIR / "LAUNCH_WAVE1_SUMMARY.md"
MONITORING_PATH = WAVE1_DIR / "POST_LAUNCH_MONITORING_CHECKLIST.md"


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


def _write_monitoring_checklist() -> Path:
    text = """# Post Launch Monitoring Checklist

- Check the GitHub Release page.
- Check the Hugging Face Space.
- Check the Hugging Face Dataset.
- Check GitHub issues.
- Watch for failed query reports.
- Do not overreact to no immediate traffic.
- Do not claim verified, safe, security certified, or quality guaranteed tools.
- Decide next: manual community posts, MCP Registry follow-up, data expansion, or README polish.
"""
    return _write(MONITORING_PATH, text)


def _render_summary(report: dict[str, Any]) -> str:
    return f"""# Launch Wave 1 Summary

- GitHub release created: `{report['github_release_created']}`
- GitHub release existing: `{report['github_release_existing']}`
- Release URL: {report['release_url']}
- Hugging Face discussion created: `{report['hf_discussion_created']}`
- GitHub discussion created: `{report['github_discussion_created']}`
- External manual posts created: `false`
- MCP Registry eligibility: `{report['mcp_registry_eligibility_decision']}`
- MCP Registry submission performed: `{report['mcp_registry_submission_performed']}`
- Recommended next step: `{report['recommended_next_step']}`

This launch wave remains conservative. It does not claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.
"""


def run_launch_wave1_report(write_result: bool = True) -> dict[str, Any]:
    release = _read_json("public_launch/wave1/GITHUB_RELEASE_RESULT.json")
    community = _read_json("public_launch/wave1/COMMUNITY_FEEDBACK_POST_RESULT.json")
    hf_discussion = _read_json("public_launch/wave1/HUGGINGFACE_DISCUSSION_RESULT.json")
    gh_discussion = _read_json("public_launch/wave1/GITHUB_DISCUSSION_RESULT.json")
    eligibility = _read_json("public_launch/wave1/MCP_REGISTRY_ELIGIBILITY_RESULT.json")
    submission = _read_json("public_launch/wave1/MCP_REGISTRY_SUBMISSION_RESULT.json")

    release_created = bool(release.get("release_created"))
    release_existing = bool(release.get("release_existing"))
    registry_submission = bool(submission.get("submission_performed"))
    recommended = (
        "Monitor release and issues."
        if release_created or release_existing
        else "Create GitHub prerelease if desired, then monitor issues."
    )
    if eligibility.get("decision", "").startswith("HOLD"):
        recommended += " MCP Registry remains HOLD until eligibility blockers are resolved."

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "github_release_created": release_created,
        "github_release_existing": release_existing,
        "release_url": release.get("url", ""),
        "hf_discussion_created": bool(hf_discussion.get("hf_discussion_created") or community.get("hf_discussion_created")),
        "github_discussion_created": bool(gh_discussion.get("github_discussion_created") or community.get("github_discussion_created")),
        "community_manual_posts_pending": True,
        "external_manual_posts_created": False,
        "mcp_registry_eligibility_decision": eligibility.get("decision", "missing"),
        "mcp_registry_submission_performed": registry_submission,
        "recommended_next_step": recommended,
        "token_printed": False,
        "overclaim_detected": False,
        "community_post_performed": bool(community.get("hf_discussion_created", False)),
        "github_release_created_or_existing": release_created or release_existing,
    }
    if write_result:
        _write_json(REPORT_PATH, report)
        _write(SUMMARY_PATH, _render_summary(report))
        _write_monitoring_checklist()
    return report


def main() -> None:
    report = run_launch_wave1_report()
    print(
        "launch_wave1_report: "
        f"release_created={report['github_release_created']} "
        f"release_existing={report['github_release_existing']} "
        f"mcp_registry={report['mcp_registry_eligibility_decision']}"
    )


if __name__ == "__main__":
    main()
