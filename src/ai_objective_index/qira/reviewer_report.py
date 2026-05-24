from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .ci_evidence_bridge import run_sample as run_qira7_sample


BundleDecision = Literal["PASS_QIRA8_REVIEWER_BUNDLE", "HOLD_QIRA8_SOURCE_ARTIFACT_MISSING"]

OUTPUT_DIR = Path("public_launch") / "qira8"
SOURCE_DIR = Path("public_launch") / "qira7"
REVIEWER_REPORT_PATH = OUTPUT_DIR / "QIRA8_REVIEWER_REPORT.md"
PR_COMMENT_DRAFT_PATH = OUTPUT_DIR / "QIRA8_PR_COMMENT_DRAFT.md"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "QIRA8_ARTIFACT_MANIFEST.json"
BUNDLE_RESULT_PATH = OUTPUT_DIR / "QIRA8_BUNDLE_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "QIRA8_NEXT_STEPS.md"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


class QiraArtifactRecord(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    path: str
    role: str
    exists: bool
    size_bytes: int = 0
    sha256: str = ""


class QiraReviewerBundleResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_ReviewerBundleResult/v0.1", alias="schema")
    decision: BundleDecision
    source_dir: str
    output_dir: str
    reviewer_report_path: str
    pr_comment_draft_path: str
    artifact_manifest_path: str
    artifact_count: int
    missing_artifacts: list[str] = Field(default_factory=list)
    review_decision: str = ""
    validation_decision: str = ""
    release_gate_decision: str = ""
    workflow_auto_enabled: bool = False
    pr_comment_posted: bool = False
    github_api_used: bool = False
    external_actions_performed: bool = False
    commands_executed_by_qira: bool = False
    patch_applied: bool = False
    merge_performed: bool = False
    deploy_performed: bool = False
    token_printed: bool = False
    generated_at: str = Field(default_factory=_timestamp)


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _read_json(relative: Path) -> dict[str, Any]:
    path = _repo_root() / relative
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _file_record(relative: Path, role: str) -> QiraArtifactRecord:
    path = _repo_root() / relative
    if not path.exists() or not path.is_file():
        return QiraArtifactRecord(path=str(relative).replace("\\", "/"), role=role, exists=False)
    data = path.read_bytes()
    return QiraArtifactRecord(
        path=str(relative).replace("\\", "/"),
        role=role,
        exists=True,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def _action_summary(action_license: dict[str, Any]) -> str:
    return f"""| Action | Decision |
| --- | --- |
| Patch draft | `{action_license.get('patch_draft', 'unknown')}` |
| PR open | `{action_license.get('pr_open', 'unknown')}` |
| Merge | `{action_license.get('merge', 'unknown')}` |
| Deploy | `{action_license.get('deploy', 'unknown')}` |
| Public claim | `{action_license.get('public_claim', 'unknown')}` |"""


def build_reviewer_markdown(review: dict[str, Any], bridge: dict[str, Any], validation: dict[str, Any]) -> str:
    release_review = review.get("release_gate_review", {})
    action = release_review.get("action_license", {})
    path_summary = release_review.get("path_summary", {})
    command_summary = release_review.get("test_command_summary", {})
    validation_decision = validation.get("decision", bridge.get("validation_decision", "unknown"))
    review_decision = review.get("decision", bridge.get("review_decision", "unknown"))
    release_decision = release_review.get("release_gate_decision", bridge.get("release_gate_decision", "unknown"))
    block_reasons = validation.get("block_reasons") or []
    hold_reasons = validation.get("hold_reasons") or []
    must_not = action.get("must_not_claim", [])
    reason_lines = "\n".join(f"- {item}" for item in block_reasons + hold_reasons) or "- No validation block or hold reasons recorded."
    must_not_lines = "\n".join(f"- {item}" for item in must_not) or "- Do not inflate this report into verification, certification, readiness, or action authorization."
    return f"""# QIRA Reviewer Report

Generated: `{_timestamp()}`

## Decision

| Field | Value |
| --- | --- |
| QIRA review | `{review_decision}` |
| CI evidence validation | `{validation_decision}` |
| Release gate | `{release_decision}` |
| Bridge decision | `{bridge.get('decision', 'unknown')}` |
| Commands executed by QIRA | `{review.get('commands_executed_by_qira', False)}` |
| GitHub API used by QIRA | `{review.get('github_api_used_by_qira', False)}` |
| PR comment posted | `False` |

## Action License

{_action_summary(action)}

Decision reason: {action.get('decision_reason', 'No action-license reason recorded.')}

## Evidence Summary

| Field | Value |
| --- | --- |
| Tests passed in supplied evidence | `{validation.get('tests_passed', False)}` |
| Accepted commands | `{validation.get('accepted_command_count', 0)}` |
| Changed files | `{path_summary.get('changed_file_count', 0)}` |
| Path categories | `{path_summary.get('category_counts', {})}` |
| Command contract | `{release_review.get('test_command_contract_decision', 'unknown')}` |
| Commands recorded | `{command_summary.get('command_count', 0)}` |

## Holds Or Blocks

{reason_lines}

## Reviewer Notes

- Scoped QIRA pass can support patch draft or PR review under recorded evidence.
- Merge, deploy, package upload, registry submission, and production use remain separately gated.
- This report is generated from local artifacts and does not post to GitHub.

## Must Not Claim

{must_not_lines}
"""


def build_pr_comment_draft(review: dict[str, Any], bridge: dict[str, Any], validation: dict[str, Any]) -> str:
    release_review = review.get("release_gate_review", {})
    action = release_review.get("action_license", {})
    return f"""## QIRA Review Draft

Decision: `{review.get('decision', bridge.get('review_decision', 'unknown'))}`

- CI evidence: `{validation.get('decision', bridge.get('validation_decision', 'unknown'))}`
- Release gate: `{release_review.get('release_gate_decision', bridge.get('release_gate_decision', 'unknown'))}`
- Patch draft: `{action.get('patch_draft', 'unknown')}`
- PR open: `{action.get('pr_open', 'unknown')}`
- Merge: `{action.get('merge', 'unknown')}`
- Deploy: `{action.get('deploy', 'unknown')}`

QIRA did not execute project commands, call GitHub APIs, post this comment, apply patches, merge, deploy, upload, publish, or handle tokens.

This is a draft only. It must not be treated as verification, security certification, quality guarantee, production readiness, or action authorization.
"""


def build_artifact_manifest(extra_paths: list[Path] | None = None) -> dict[str, Any]:
    records = [
        _file_record(SOURCE_DIR / "QIRA7_SAMPLE_TASK_PACKET.json", "source_task_packet"),
        _file_record(SOURCE_DIR / "QIRA7_CI_EVIDENCE.json", "ci_evidence"),
        _file_record(SOURCE_DIR / "QIRA7_VALIDATION_RESULT.json", "validation"),
        _file_record(SOURCE_DIR / "QIRA7_REVIEW_RESULT.json", "review"),
        _file_record(SOURCE_DIR / "QIRA7_BRIDGE_RESULT.json", "bridge_result"),
    ]
    for path in extra_paths or []:
        records.append(_file_record(path, "qira8_output"))
    missing = [record.path for record in records if not record.exists]
    return {
        "schema": "QIRA_ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_QIRA8_ARTIFACT_MANIFEST" if not missing else "HOLD_QIRA8_ARTIFACT_MISSING",
        "artifacts": [record.model_dump(mode="json") for record in records],
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "github_api_used": False,
        "pr_comment_posted": False,
        "token_printed": False,
    }


def build_qira8_bundle(run_upstream_sample: bool = True) -> QiraReviewerBundleResult:
    if run_upstream_sample:
        run_qira7_sample()
    review = _read_json(SOURCE_DIR / "QIRA7_REVIEW_RESULT.json")
    bridge = _read_json(SOURCE_DIR / "QIRA7_BRIDGE_RESULT.json")
    validation = _read_json(SOURCE_DIR / "QIRA7_VALIDATION_RESULT.json")
    report = build_reviewer_markdown(review, bridge, validation)
    comment = build_pr_comment_draft(review, bridge, validation)
    _write_text(REVIEWER_REPORT_PATH, report)
    _write_text(PR_COMMENT_DRAFT_PATH, comment)
    manifest = build_artifact_manifest([REVIEWER_REPORT_PATH, PR_COMMENT_DRAFT_PATH])
    _write_json(ARTIFACT_MANIFEST_PATH, manifest)
    _write_text(
        NEXT_STEPS_PATH,
        """# QIRA-8 Next Steps

1. Attach the reviewer report and artifact manifest to an opt-in workflow artifact.
2. Add an optional PR-comment posting gate only after explicit repository-owner opt-in.
3. Keep QIRA report generation separate from merge, deploy, upload, publish, and production readiness decisions.
""",
    )
    missing = manifest["missing_artifacts"]
    result = QiraReviewerBundleResult(
        decision="HOLD_QIRA8_SOURCE_ARTIFACT_MISSING" if missing else "PASS_QIRA8_REVIEWER_BUNDLE",
        source_dir=str(SOURCE_DIR).replace("\\", "/"),
        output_dir=str(OUTPUT_DIR).replace("\\", "/"),
        reviewer_report_path=str(REVIEWER_REPORT_PATH).replace("\\", "/"),
        pr_comment_draft_path=str(PR_COMMENT_DRAFT_PATH).replace("\\", "/"),
        artifact_manifest_path=str(ARTIFACT_MANIFEST_PATH).replace("\\", "/"),
        artifact_count=len(manifest["artifacts"]),
        missing_artifacts=missing,
        review_decision=review.get("decision", ""),
        validation_decision=validation.get("decision", bridge.get("validation_decision", "")),
        release_gate_decision=review.get("release_gate_review", {}).get("release_gate_decision", bridge.get("release_gate_decision", "")),
    )
    _write_json(BUNDLE_RESULT_PATH, result.model_dump(mode="json", by_alias=True))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a QIRA reviewer report and artifact manifest from local QIRA artifacts.")
    parser.add_argument("--run-sample", action="store_true", help="Regenerate QIRA-7 sample artifacts and build QIRA-8 outputs.")
    parser.add_argument("--no-upstream-sample", action="store_true", help="Use existing QIRA-7 artifacts without regenerating them.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = build_qira8_bundle(run_upstream_sample=args.run_sample or not args.no_upstream_sample)
    print(f"qira_reviewer_report: {result.decision} artifacts={result.artifact_count}")


if __name__ == "__main__":
    main()
