from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .package5 import run_datacapsule5_package


BundleDecision = Literal["PASS_DATACAPSULE6_REPOSITORY_AUDIT_BUNDLE", "HOLD_DATACAPSULE6_SOURCE_ARTIFACT_MISSING"]

OUTPUT_DIR = Path("public_launch") / "datacapsule6"
SOURCE_DIR = Path("public_launch") / "datacapsule5"
CORPUS_AUDIT_REPORT_PATH = OUTPUT_DIR / "DATACAPSULE6_CORPUS_AUDIT_REPORT.md"
REVIEW_COMMENT_DRAFT_PATH = OUTPUT_DIR / "DATACAPSULE6_REVIEW_COMMENT_DRAFT.md"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "DATACAPSULE6_ARTIFACT_MANIFEST.json"
BUNDLE_RESULT_PATH = OUTPUT_DIR / "DATACAPSULE6_BUNDLE_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "DATACAPSULE6_NEXT_STEPS.md"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


class DataCapsuleArtifactRecord(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    path: str
    role: str
    exists: bool
    size_bytes: int = 0
    sha256: str = ""


class DataCapsuleRepositoryAuditBundleResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="DataCapsule_RepositoryAuditBundleResult/v0.1", alias="schema")
    decision: BundleDecision
    source_dir: str
    output_dir: str
    corpus_audit_report_path: str
    review_comment_draft_path: str
    artifact_manifest_path: str
    artifact_count: int
    missing_artifacts: list[str] = Field(default_factory=list)
    datacapsule5_package_decision: str = ""
    fixture_corpus_decision: str = ""
    negative_control_decision: str = ""
    fixture_count: int = 0
    false_pass_count: int = 0
    mismatch_count: int = 0
    actual_counts: dict[str, int] = Field(default_factory=dict)
    review_comment_posted: bool = False
    github_api_used: bool = False
    crawler_used: bool = False
    network_used: bool = False
    external_service_used: bool = False
    external_actions_performed: bool = False
    token_printed: bool = False
    can_certify_rights: bool = False
    can_certify_privacy: bool = False
    can_certify_quality: bool = False
    can_prove_eval_cleanliness: bool = False
    can_authorize_action: bool = False
    known_limits: list[str] = Field(default_factory=list)
    must_not_claim: list[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=_timestamp)


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _read_json(relative: Path) -> dict[str, Any]:
    path = _repo_root() / relative
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _file_record(relative: Path, role: str) -> DataCapsuleArtifactRecord:
    path = _repo_root() / relative
    normalized = str(relative).replace("\\", "/")
    if not path.exists() or not path.is_file():
        return DataCapsuleArtifactRecord(path=normalized, role=role, exists=False)
    data = path.read_bytes()
    return DataCapsuleArtifactRecord(
        path=normalized,
        role=role,
        exists=True,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def _fixture_rows(corpus: dict[str, Any]) -> str:
    rows = []
    for item in corpus.get("fixtures", []):
        rows.append(
            "| `{fixture}` | `{use}` | `{theme}` | `{decision}` |".format(
                fixture=item.get("fixture_id", "unknown"),
                use=item.get("primary_use", "unknown"),
                theme=item.get("risk_theme", "unknown"),
                decision=item.get("expected_decision", "unknown"),
            )
        )
    return "\n".join(rows) or "| `none` | `unknown` | `unknown` | `unknown` |"


def _negative_control_rows(negative_controls: dict[str, Any]) -> str:
    rows = []
    for item in negative_controls.get("results", []):
        rows.append(
            "| `{fixture}` | `{expected}` | `{actual}` | `{false_pass}` |".format(
                fixture=item.get("fixture_id", "unknown"),
                expected=item.get("expected_decision", "unknown"),
                actual=item.get("actual_decision", "unknown"),
                false_pass=item.get("false_pass", "unknown"),
            )
        )
    return "\n".join(rows) or "| `none` | `unknown` | `unknown` | `unknown` |"


def _must_not_claim_lines() -> str:
    claims = [
        "legal sufficiency",
        "privacy compliance",
        "data quality guarantee",
        "license clearance",
        "evaluation cleanliness",
        "purchasing advice",
        "action authorization",
    ]
    return "\n".join(f"- Do not claim {item}." for item in claims)


def build_corpus_audit_markdown(package: dict[str, Any], corpus: dict[str, Any], negative_controls: dict[str, Any]) -> str:
    actual_counts = negative_controls.get("actual_counts", package.get("actual_counts", {})) or {}
    return f"""# DataCapsule-6 Repository Corpus Audit Report

Generated: `{_timestamp()}`

DataCapsule-6 packages local DataCapsule-5 fixture corpus and negative-control outputs into reviewer-facing artifacts. It is for human review of repository-supplied data-use metadata patterns.

## Decision

| Field | Value |
| --- | --- |
| DataCapsule-6 bundle | `PASS_DATACAPSULE6_REPOSITORY_AUDIT_BUNDLE` |
| DataCapsule-5 package | `{package.get('decision', 'unknown')}` |
| Fixture corpus | `{corpus.get('decision', package.get('fixture_corpus_decision', 'unknown'))}` |
| Negative controls | `{negative_controls.get('decision', package.get('negative_control_decision', 'unknown'))}` |
| Fixtures | `{corpus.get('fixture_count', package.get('fixture_count', 0))}` |
| Actual ALLOW | `{actual_counts.get('allow', 0)}` |
| Actual HOLD | `{actual_counts.get('hold', 0)}` |
| Actual BLOCK | `{actual_counts.get('block', 0)}` |
| False passes | `{negative_controls.get('false_pass_count', package.get('false_pass_count', 0))}` |
| Mismatches | `{negative_controls.get('mismatch_count', package.get('mismatch_count', 0))}` |
| Crawler used | `False` |
| Network used | `False` |
| External service used | `False` |
| Review comment posted | `False` |

## Fixture Corpus

| Fixture | Primary Use | Risk Theme | Expected Decision |
| --- | --- | --- | --- |
{_fixture_rows(corpus)}

## Negative-Control Outcomes

| Fixture | Expected | Actual | False Pass |
| --- | --- | --- | --- |
{_negative_control_rows(negative_controls)}

## Reviewer Notes

- `ALLOW_USE` means the local public metadata fixture did not trigger a hold or block for that requested use.
- `HOLD_*` means the metadata needs source, rights, privacy, prompt-injection, or eval-leak review before use.
- `BLOCK_*` means the metadata is unsuitable for the requested use under the public local rules.
- This report is generated from local artifacts and does not crawl directories, inspect private file contents, fetch URLs, call external services, post comments, or handle tokens.

## Must Not Claim

{_must_not_claim_lines()}
"""


def build_review_comment_draft(package: dict[str, Any], corpus: dict[str, Any], negative_controls: dict[str, Any]) -> str:
    actual_counts = negative_controls.get("actual_counts", package.get("actual_counts", {})) or {}
    return f"""## DataCapsule Corpus Audit Draft

Decision: `{package.get('decision', 'unknown')}`

- Fixture corpus: `{corpus.get('decision', package.get('fixture_corpus_decision', 'unknown'))}`
- Negative controls: `{negative_controls.get('decision', package.get('negative_control_decision', 'unknown'))}`
- Fixtures reviewed as local metadata: `{corpus.get('fixture_count', package.get('fixture_count', 0))}`
- Actual counts: `ALLOW={actual_counts.get('allow', 0)} HOLD={actual_counts.get('hold', 0)} BLOCK={actual_counts.get('block', 0)}`
- False passes: `{negative_controls.get('false_pass_count', package.get('false_pass_count', 0))}`

This is a draft only. DataCapsule did not post this comment, crawl directories, inspect private file contents, fetch URLs, call external services, handle tokens, prove rights, certify privacy, guarantee data quality, prove evaluation cleanliness, clear licenses, or authorize actions.

Reviewer follow-up:
- Review every HOLD item before using the corpus for training, retrieval, evaluation, summarization, sharing, or action-related workflows.
- Treat BLOCK items as unsuitable for the requested use unless metadata and policy are changed and reviewed again.
- Keep private scoring policy, receipt weighting, private negative-control banks, and commercial data strategy outside this public artifact.
"""


def build_artifact_manifest(extra_paths: list[Path] | None = None) -> dict[str, Any]:
    records = [
        _file_record(SOURCE_DIR / "DATACAPSULE5_FIXTURE_CORPUS.json", "fixture_corpus"),
        _file_record(SOURCE_DIR / "DATACAPSULE5_FIXTURE_CORPUS_REPORT.md", "fixture_corpus_report"),
        _file_record(SOURCE_DIR / "DATACAPSULE5_NEGATIVE_CONTROL_RESULT.json", "negative_control_result"),
        _file_record(SOURCE_DIR / "DATACAPSULE5_NEGATIVE_CONTROL_REPORT.md", "negative_control_report"),
        _file_record(SOURCE_DIR / "DATACAPSULE5_PACKAGE_RESULT.json", "package_result"),
    ]
    for path in extra_paths or []:
        records.append(_file_record(path, "datacapsule6_output"))
    missing = [record.path for record in records if not record.exists]
    return {
        "schema": "DataCapsule_ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_DATACAPSULE6_ARTIFACT_MANIFEST" if not missing else "HOLD_DATACAPSULE6_ARTIFACT_MISSING",
        "artifacts": [record.model_dump(mode="json") for record in records],
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "review_comment_posted": False,
        "github_api_used": False,
        "crawler_used": False,
        "network_used": False,
        "external_service_used": False,
        "token_printed": False,
    }


def build_datacapsule6_bundle(run_upstream_sample: bool = True) -> DataCapsuleRepositoryAuditBundleResult:
    if run_upstream_sample:
        run_datacapsule5_package()
    package = _read_json(SOURCE_DIR / "DATACAPSULE5_PACKAGE_RESULT.json")
    corpus = _read_json(SOURCE_DIR / "DATACAPSULE5_FIXTURE_CORPUS.json")
    negative_controls = _read_json(SOURCE_DIR / "DATACAPSULE5_NEGATIVE_CONTROL_RESULT.json")
    _write_text(CORPUS_AUDIT_REPORT_PATH, build_corpus_audit_markdown(package, corpus, negative_controls))
    _write_text(REVIEW_COMMENT_DRAFT_PATH, build_review_comment_draft(package, corpus, negative_controls))
    manifest = build_artifact_manifest([CORPUS_AUDIT_REPORT_PATH, REVIEW_COMMENT_DRAFT_PATH])
    _write_json(ARTIFACT_MANIFEST_PATH, manifest)
    _write_text(
        NEXT_STEPS_PATH,
        """# DataCapsule-6 Next Steps

1. Attach the corpus audit report and artifact manifest to an opt-in repository workflow artifact.
2. Add optional review-comment posting only after explicit repository-owner opt-in.
3. Keep DataCapsule audit artifacts separate from crawling, private file-content inspection, legal review, privacy certification, data-quality claims, license clearance, evaluation-cleanliness proof, and action authorization.
""",
    )
    missing = manifest["missing_artifacts"]
    actual_counts = negative_controls.get("actual_counts", package.get("actual_counts", {})) or {}
    result = DataCapsuleRepositoryAuditBundleResult(
        decision="HOLD_DATACAPSULE6_SOURCE_ARTIFACT_MISSING" if missing else "PASS_DATACAPSULE6_REPOSITORY_AUDIT_BUNDLE",
        source_dir=str(SOURCE_DIR).replace("\\", "/"),
        output_dir=str(OUTPUT_DIR).replace("\\", "/"),
        corpus_audit_report_path=str(CORPUS_AUDIT_REPORT_PATH).replace("\\", "/"),
        review_comment_draft_path=str(REVIEW_COMMENT_DRAFT_PATH).replace("\\", "/"),
        artifact_manifest_path=str(ARTIFACT_MANIFEST_PATH).replace("\\", "/"),
        artifact_count=len(manifest["artifacts"]),
        missing_artifacts=missing,
        datacapsule5_package_decision=package.get("decision", ""),
        fixture_corpus_decision=corpus.get("decision", package.get("fixture_corpus_decision", "")),
        negative_control_decision=negative_controls.get("decision", package.get("negative_control_decision", "")),
        fixture_count=int(corpus.get("fixture_count", package.get("fixture_count", 0)) or 0),
        false_pass_count=int(negative_controls.get("false_pass_count", package.get("false_pass_count", 0)) or 0),
        mismatch_count=int(negative_controls.get("mismatch_count", package.get("mismatch_count", 0)) or 0),
        actual_counts={
            "allow": int(actual_counts.get("allow", 0) or 0),
            "hold": int(actual_counts.get("hold", 0) or 0),
            "block": int(actual_counts.get("block", 0) or 0),
        },
        known_limits=[
            "repository-owned local metadata artifact bundle only",
            "public-safe fake data-use fixtures only",
            "local negative controls only",
            "no crawling",
            "no live source verification",
            "no private data inspection",
            "not legal sufficiency",
            "not privacy compliance",
            "not data quality guarantee",
            "not evaluation cleanliness proof",
            "not action authorization",
        ],
        must_not_claim=[
            "do not claim legal sufficiency",
            "do not claim privacy compliance",
            "do not claim data quality guarantee",
            "do not claim license clearance",
            "do not claim evaluation cleanliness",
            "do not claim action authorization",
            "do not claim purchasing advice",
        ],
    )
    _write_json(BUNDLE_RESULT_PATH, result.model_dump(mode="json", by_alias=True))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build DataCapsule repository corpus audit artifacts from local DataCapsule-5 outputs.")
    parser.add_argument("--run-sample", action="store_true", help="Regenerate DataCapsule-5 sample artifacts and build DataCapsule-6 outputs.")
    parser.add_argument("--no-upstream-sample", action="store_true", help="Use existing DataCapsule-5 artifacts without regenerating them.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = build_datacapsule6_bundle(run_upstream_sample=args.run_sample or not args.no_upstream_sample)
    print(f"datacapsule6_repository_audit_bundle: {result.decision} artifacts={result.artifact_count}")


if __name__ == "__main__":
    main()
