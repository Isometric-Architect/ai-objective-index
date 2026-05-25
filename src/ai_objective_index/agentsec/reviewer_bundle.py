from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .package6 import run_agentsec6_package


BundleDecision = Literal["PASS_AGENTSEC7_REVIEWER_BUNDLE", "HOLD_AGENTSEC7_SOURCE_ARTIFACT_MISSING"]

OUTPUT_DIR = Path("public_launch") / "agentsec7"
SOURCE_DIR = Path("public_launch") / "agentsec6"
REVIEWER_REPORT_PATH = OUTPUT_DIR / "AGENTSEC7_REVIEWER_REPORT.md"
PR_COMMENT_DRAFT_PATH = OUTPUT_DIR / "AGENTSEC7_PR_COMMENT_DRAFT.md"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "AGENTSEC7_ARTIFACT_MANIFEST.json"
BUNDLE_RESULT_PATH = OUTPUT_DIR / "AGENTSEC7_BUNDLE_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "AGENTSEC7_NEXT_STEPS.md"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


class AgentSecArtifactRecord(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    path: str
    role: str
    exists: bool
    size_bytes: int = 0
    sha256: str = ""


class AgentSecReviewerBundleResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AgentSec_ReviewerBundleResult/v0.1", alias="schema")
    decision: BundleDecision
    source_dir: str
    output_dir: str
    reviewer_report_path: str
    pr_comment_draft_path: str
    artifact_manifest_path: str
    artifact_count: int
    missing_artifacts: list[str] = Field(default_factory=list)
    agentsec6_package_decision: str = ""
    corpus_intake_decision: str = ""
    policy_gate_decision: str = ""
    manifest_count: int = 0
    allow_count: int = 0
    hold_count: int = 0
    block_count: int = 0
    workflow_auto_enabled: bool = False
    pr_comment_posted: bool = False
    github_api_used: bool = False
    external_actions_performed: bool = False
    live_mcp_called: bool = False
    external_tool_executed: bool = False
    network_used: bool = False
    token_printed: bool = False
    can_certify_security: bool = False
    can_certify_quality: bool = False
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


def _file_record(relative: Path, role: str) -> AgentSecArtifactRecord:
    path = _repo_root() / relative
    normalized = str(relative).replace("\\", "/")
    if not path.exists() or not path.is_file():
        return AgentSecArtifactRecord(path=normalized, role=role, exists=False)
    data = path.read_bytes()
    return AgentSecArtifactRecord(
        path=normalized,
        role=role,
        exists=True,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def _packet_rows(policy_gate: dict[str, Any]) -> str:
    rows = []
    for packet in policy_gate.get("packets", []):
        rows.append(
            "| `{tool}` | `{decision}` | `{integration}` | `{provider}` |".format(
                tool=packet.get("tool_id", "unknown"),
                decision=packet.get("risk_decision", "unknown"),
                integration=packet.get("integration_type", "unknown"),
                provider=packet.get("provider", "unknown"),
            )
        )
    return "\n".join(rows) or "| `none` | `unknown` | `unknown` | `unknown` |"


def _reason_lines(policy_gate: dict[str, Any], field_name: str) -> str:
    reasons: list[str] = []
    for packet in policy_gate.get("packets", []):
        tool_id = packet.get("tool_id", "unknown")
        for reason in packet.get(field_name, []) or []:
            reasons.append(f"- `{tool_id}`: {reason}")
    return "\n".join(reasons) or "- No reasons recorded."


def _must_not_claim_lines() -> str:
    claims = [
        "verified tool status",
        "safety",
        "security certification",
        "quality guarantee",
        "production readiness",
        "live gateway protection",
        "external action authorization",
        "legal compliance",
    ]
    return "\n".join(f"- Do not claim {item}." for item in claims)


def build_reviewer_markdown(package: dict[str, Any], intake: dict[str, Any], policy_gate: dict[str, Any]) -> str:
    return f"""# AgentSec-7 Reviewer Report

Generated: `{_timestamp()}`

AgentSec-7 packages the AgentSec-6 local manifest corpus result into reviewer-facing artifacts. It is meant for human review and optional repository-owned workflow artifacts.

## Decision

| Field | Value |
| --- | --- |
| AgentSec-7 bundle | `PASS_AGENTSEC7_REVIEWER_BUNDLE` |
| AgentSec-6 package | `{package.get('decision', 'unknown')}` |
| Corpus intake | `{intake.get('decision', package.get('corpus_intake_decision', 'unknown'))}` |
| Policy gate | `{policy_gate.get('decision', intake.get('policy_gate_decision', 'unknown'))}` |
| Manifests | `{intake.get('manifest_count', package.get('manifest_count', 0))}` |
| ALLOW metadata-only | `{intake.get('allow_count', package.get('allow_count', 0))}` |
| HOLD review | `{intake.get('hold_count', package.get('hold_count', 0))}` |
| BLOCK policy risk | `{intake.get('block_count', package.get('block_count', 0))}` |
| GitHub API used | `False` |
| PR comment posted | `False` |
| Live MCP calls | `False` |
| External tool execution | `False` |
| URL fetch | `False` |

## Packet Decisions

| Tool | Decision | Integration | Provider |
| --- | --- | --- | --- |
{_packet_rows(policy_gate)}

## Hold Reasons

{_reason_lines(policy_gate, 'policy_hold_reasons')}

## Block Reasons

{_reason_lines(policy_gate, 'policy_block_reasons')}

## Reviewer Notes

- `ALLOW_METADATA_ONLY` means the local metadata profile did not detect a blocking pattern in the supplied fixture or manifest.
- `HOLD_REVIEW_REQUIRED` means the supplied metadata needs human or policy review before use.
- `BLOCK_POLICY_RISK` means the local metadata carries a forbidden action or unsupported claim pattern.
- This report is generated from local artifacts and does not post to GitHub, call live MCP servers, execute tools, fetch URLs, or handle tokens.

## Must Not Claim

{_must_not_claim_lines()}
"""


def build_pr_comment_draft(package: dict[str, Any], intake: dict[str, Any], policy_gate: dict[str, Any]) -> str:
    hold_count = intake.get("hold_count", package.get("hold_count", 0))
    block_count = intake.get("block_count", package.get("block_count", 0))
    return f"""## AgentSec Review Draft

Decision: `{package.get('decision', 'unknown')}`

- Corpus intake: `{intake.get('decision', package.get('corpus_intake_decision', 'unknown'))}`
- Policy gate: `{policy_gate.get('decision', intake.get('policy_gate_decision', 'unknown'))}`
- Manifests reviewed as local metadata: `{intake.get('manifest_count', package.get('manifest_count', 0))}`
- ALLOW metadata-only: `{intake.get('allow_count', package.get('allow_count', 0))}`
- HOLD review: `{hold_count}`
- BLOCK policy risk: `{block_count}`

This is a draft only. AgentSec did not post this comment, call live MCP servers, execute tools, fetch URLs, call GitHub APIs, handle tokens, certify security, guarantee quality, prove product readiness, or authorize external actions.

Reviewer follow-up:
- Review every HOLD item before use.
- Treat BLOCK items as unsuitable for the requested scope unless the manifest or policy is changed and reviewed again.
- Keep private thresholds, provider priors, anti-gaming rules, and private negative-control banks outside this public artifact.
"""


def build_artifact_manifest(extra_paths: list[Path] | None = None) -> dict[str, Any]:
    records = [
        _file_record(SOURCE_DIR / "AGENTSEC6_SAMPLE_MANIFEST_CORPUS.json", "source_manifest_corpus"),
        _file_record(SOURCE_DIR / "AGENTSEC6_CORPUS_INTAKE_RESULT.json", "corpus_intake"),
        _file_record(SOURCE_DIR / "AGENTSEC6_POLICY_GATE_RESULT.json", "policy_gate"),
        _file_record(SOURCE_DIR / "AGENTSEC6_CORPUS_REPORT.md", "corpus_report"),
        _file_record(SOURCE_DIR / "AGENTSEC6_PACKAGE_RESULT.json", "package_result"),
    ]
    for path in extra_paths or []:
        records.append(_file_record(path, "agentsec7_output"))
    missing = [record.path for record in records if not record.exists]
    return {
        "schema": "AgentSec_ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_AGENTSEC7_ARTIFACT_MANIFEST" if not missing else "HOLD_AGENTSEC7_ARTIFACT_MISSING",
        "artifacts": [record.model_dump(mode="json") for record in records],
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "github_api_used": False,
        "pr_comment_posted": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "network_used": False,
        "token_printed": False,
    }


def build_agentsec7_bundle(run_upstream_sample: bool = True) -> AgentSecReviewerBundleResult:
    if run_upstream_sample:
        run_agentsec6_package()
    package = _read_json(SOURCE_DIR / "AGENTSEC6_PACKAGE_RESULT.json")
    intake = _read_json(SOURCE_DIR / "AGENTSEC6_CORPUS_INTAKE_RESULT.json")
    policy_gate = _read_json(SOURCE_DIR / "AGENTSEC6_POLICY_GATE_RESULT.json")
    _write_text(REVIEWER_REPORT_PATH, build_reviewer_markdown(package, intake, policy_gate))
    _write_text(PR_COMMENT_DRAFT_PATH, build_pr_comment_draft(package, intake, policy_gate))
    manifest = build_artifact_manifest([REVIEWER_REPORT_PATH, PR_COMMENT_DRAFT_PATH])
    _write_json(ARTIFACT_MANIFEST_PATH, manifest)
    _write_text(
        NEXT_STEPS_PATH,
        """# AgentSec-7 Next Steps

1. Attach the reviewer report and artifact manifest to an opt-in repository workflow artifact.
2. Add optional PR-comment posting only after explicit repository-owner opt-in.
3. Keep AgentSec review artifacts separate from live MCP execution, external tool execution, security certification, product-readiness claims, and action authorization.
""",
    )
    missing = manifest["missing_artifacts"]
    result = AgentSecReviewerBundleResult(
        decision="HOLD_AGENTSEC7_SOURCE_ARTIFACT_MISSING" if missing else "PASS_AGENTSEC7_REVIEWER_BUNDLE",
        source_dir=str(SOURCE_DIR).replace("\\", "/"),
        output_dir=str(OUTPUT_DIR).replace("\\", "/"),
        reviewer_report_path=str(REVIEWER_REPORT_PATH).replace("\\", "/"),
        pr_comment_draft_path=str(PR_COMMENT_DRAFT_PATH).replace("\\", "/"),
        artifact_manifest_path=str(ARTIFACT_MANIFEST_PATH).replace("\\", "/"),
        artifact_count=len(manifest["artifacts"]),
        missing_artifacts=missing,
        agentsec6_package_decision=package.get("decision", ""),
        corpus_intake_decision=intake.get("decision", package.get("corpus_intake_decision", "")),
        policy_gate_decision=policy_gate.get("decision", intake.get("policy_gate_decision", "")),
        manifest_count=int(intake.get("manifest_count", package.get("manifest_count", 0)) or 0),
        allow_count=int(intake.get("allow_count", package.get("allow_count", 0)) or 0),
        hold_count=int(intake.get("hold_count", package.get("hold_count", 0)) or 0),
        block_count=int(intake.get("block_count", package.get("block_count", 0)) or 0),
        known_limits=[
            "local manifest artifact bundle only",
            "no live MCP call",
            "no external tool execution",
            "no URL fetch",
            "no GitHub API call",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not product-readiness proof",
            "not action authorization",
        ],
        must_not_claim=[
            "do not claim verified tool status",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim live gateway protection",
            "do not claim external action authorization",
            "do not claim legal compliance",
        ],
    )
    _write_json(BUNDLE_RESULT_PATH, result.model_dump(mode="json", by_alias=True))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build AgentSec reviewer report artifacts from local AgentSec-6 outputs.")
    parser.add_argument("--run-sample", action="store_true", help="Regenerate AgentSec-6 sample artifacts and build AgentSec-7 outputs.")
    parser.add_argument("--no-upstream-sample", action="store_true", help="Use existing AgentSec-6 artifacts without regenerating them.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = build_agentsec7_bundle(run_upstream_sample=args.run_sample or not args.no_upstream_sample)
    print(f"agentsec7_reviewer_bundle: {result.decision} artifacts={result.artifact_count}")


if __name__ == "__main__":
    main()
