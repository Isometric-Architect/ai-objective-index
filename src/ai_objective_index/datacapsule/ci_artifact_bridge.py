from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .manifest_intake import (
    SAMPLE_CSV_TEXT,
    build_manifest_intake_report,
    build_manifest_intake_result,
    load_manifest_table,
    rows_to_corpus_manifest,
)


BridgeDecision = Literal[
    "PASS_DATACAPSULE4_CI_ARTIFACT_BRIDGE",
    "HOLD_DATACAPSULE4_MANIFEST_REQUIRED",
    "HOLD_DATACAPSULE4_REVIEW_REQUIRED",
    "BLOCK_DATACAPSULE4_USE_RISK",
]

OUTPUT_DIR = Path("public_launch") / "datacapsule4"
SAMPLE_MANIFEST_PATH = OUTPUT_DIR / "DATACAPSULE4_SAMPLE_MANIFEST.csv"
NORMALIZED_MANIFEST_PATH = OUTPUT_DIR / "DATACAPSULE4_NORMALIZED_MANIFEST.json"
CORPUS_CAPSULE_PATH = OUTPUT_DIR / "DATACAPSULE4_CORPUS_CAPSULE.json"
CORPUS_RESULT_PATH = OUTPUT_DIR / "DATACAPSULE4_CORPUS_RESULT.json"
EVAL_LEAK_REPORT_PATH = OUTPUT_DIR / "DATACAPSULE4_EVAL_LEAK_SEPARATION_REPORT.json"
INTAKE_RESULT_PATH = OUTPUT_DIR / "DATACAPSULE4_INTAKE_RESULT.json"
BRIDGE_RESULT_PATH = OUTPUT_DIR / "DATACAPSULE4_BRIDGE_RESULT.json"
BRIDGE_REPORT_PATH = OUTPUT_DIR / "DATACAPSULE4_BRIDGE_REPORT.md"
ACTION_MANIFEST_AUDIT_PATH = OUTPUT_DIR / "DATACAPSULE4_ACTION_MANIFEST_AUDIT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "DATACAPSULE4_NEXT_STEPS.md"


class DataCapsuleCiArtifactBridgeRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="DataCapsule_CiArtifactBridgeRequest/v0.1", alias="schema")
    manifest_path: str = ""
    output_dir: str = str(OUTPUT_DIR)
    corpus_id: str = "repository.local/corpus"
    name: str = "Repository local corpus manifest"
    source: str = "github_actions"
    workflow_name: str = "DataCapsule Corpus Manifest Artifact Bridge"
    job_name: str = "datacapsule-corpus-manifest"
    commit_sha: str = ""
    branch: str = ""
    declared_claims: list[str] = Field(
        default_factory=lambda: ["Repository-supplied corpus manifest metadata for scoped DataCapsule local review only."]
    )


class DataCapsuleCiArtifactBridgeResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="DataCapsule_CiArtifactBridgeResult/v0.1", alias="schema")
    decision: BridgeDecision
    intake_decision: str
    eval_leak_decision: str = "not_checked"
    manifest_path: str
    output_dir: str
    intake_result_path: str
    bridge_report_path: str
    workflow_auto_enabled: bool = False
    active_workflow_created: bool = False
    external_actions_performed: bool = False
    github_api_used_by_datacapsule: bool = False
    directory_crawled: bool = False
    private_file_contents_read: bool = False
    url_fetch_performed: bool = False
    external_service_used: bool = False
    token_printed: bool = False
    can_certify_rights: bool = False
    can_certify_privacy: bool = False
    can_certify_quality: bool = False
    can_prove_eval_cleanliness: bool = False
    can_authorize_action: bool = False
    known_limits: list[str] = Field(default_factory=list)


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _resolve_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    if path.is_absolute():
        try:
            return path.relative_to(_repo_root())
        except ValueError as exc:
            raise ValueError("DataCapsule-4 output directory must be inside the repository.") from exc
    return path


def _bridge_paths(output_dir: Path) -> dict[str, Path]:
    return {
        "normalized": output_dir / "DATACAPSULE4_NORMALIZED_MANIFEST.json",
        "capsule": output_dir / "DATACAPSULE4_CORPUS_CAPSULE.json",
        "corpus_result": output_dir / "DATACAPSULE4_CORPUS_RESULT.json",
        "eval_report": output_dir / "DATACAPSULE4_EVAL_LEAK_SEPARATION_REPORT.json",
        "intake_result": output_dir / "DATACAPSULE4_INTAKE_RESULT.json",
        "bridge_result": output_dir / "DATACAPSULE4_BRIDGE_RESULT.json",
        "bridge_report": output_dir / "DATACAPSULE4_BRIDGE_REPORT.md",
        "next_steps": output_dir / "DATACAPSULE4_NEXT_STEPS.md",
    }


def _bridge_decision(intake_decision: str) -> BridgeDecision:
    if intake_decision.startswith("BLOCK"):
        return "BLOCK_DATACAPSULE4_USE_RISK"
    if intake_decision.startswith("HOLD"):
        return "HOLD_DATACAPSULE4_REVIEW_REQUIRED"
    return "PASS_DATACAPSULE4_CI_ARTIFACT_BRIDGE"


def write_next_steps(output_dir: Path = OUTPUT_DIR) -> Path:
    return _write_text(
        output_dir / "DATACAPSULE4_NEXT_STEPS.md",
        """# DataCapsule-4 Next Steps

1. Keep the workflow example in `examples/` until the repository owner opts in.
2. Feed repository-supplied CSV, JSONL, or JSON corpus manifests into the bridge from normal CI.
3. Publish DataCapsule JSON/Markdown outputs as workflow artifacts only if the repository owner wants them.
4. Keep live crawling, private file inspection, rights/privacy certification, and action authorization separately gated.

DataCapsule-4 does not crawl directories, read private file contents, fetch URLs, call GitHub APIs, handle tokens, prove legal sufficiency, prove privacy compliance, guarantee data quality, prove evaluation cleanliness, or authorize actions.
""",
    )


def build_bridge_report(result: DataCapsuleCiArtifactBridgeResult) -> str:
    return f"""# DataCapsule-4 CI Artifact Bridge Report

Decision: `{result.decision}`

| Field | Value |
| --- | --- |
| Intake decision | `{result.intake_decision}` |
| Eval-leak decision | `{result.eval_leak_decision}` |
| Manifest path | `{result.manifest_path}` |
| Workflow auto-enabled | `False` |
| Active workflow created | `False` |
| Directory crawled | `False` |
| Private file contents read | `False` |
| URL fetch performed | `False` |
| GitHub API used by DataCapsule | `False` |
| Token printed | `False` |

DataCapsule-4 converts opt-in CI corpus manifest metadata into local DataCapsule artifacts. It does not prove rights, privacy compliance, data quality, evaluation cleanliness, security, product readiness, or action authorization.
"""


def run_ci_artifact_bridge(request: DataCapsuleCiArtifactBridgeRequest) -> DataCapsuleCiArtifactBridgeResult:
    output_dir = _resolve_output_dir(request.output_dir)
    paths = _bridge_paths(output_dir)
    if not request.manifest_path:
        result = DataCapsuleCiArtifactBridgeResult(
            decision="HOLD_DATACAPSULE4_MANIFEST_REQUIRED",
            intake_decision="not_checked",
            manifest_path="",
            output_dir=str(output_dir).replace("\\", "/"),
            intake_result_path=str(paths["intake_result"]).replace("\\", "/"),
            bridge_report_path=str(paths["bridge_report"]).replace("\\", "/"),
            known_limits=["A local CSV, JSONL, or JSON corpus manifest path is required."],
        )
        _write_json(paths["bridge_result"], result.model_dump(mode="json", by_alias=True))
        _write_text(paths["bridge_report"], build_bridge_report(result))
        write_next_steps(output_dir)
        return result

    source_format, rows = load_manifest_table(Path(request.manifest_path))
    normalized = rows_to_corpus_manifest(rows, request.corpus_id, request.name, source_format)
    _write_json(paths["normalized"], normalized)
    intake = build_manifest_intake_result(
        Path(request.manifest_path),
        corpus_id=request.corpus_id,
        name=request.name,
        normalized_manifest_path=paths["normalized"],
        corpus_capsule_path=paths["capsule"],
        corpus_result_path=paths["corpus_result"],
        eval_leak_report_path=paths["eval_report"],
        report_path=paths["bridge_report"],
    )
    _write_json(paths["capsule"], intake.corpus_result.capsule.model_dump(mode="json", by_alias=True))
    _write_json(paths["corpus_result"], intake.corpus_result.model_dump(mode="json", by_alias=True))
    _write_json(paths["eval_report"], intake.eval_leak_report.model_dump(mode="json", by_alias=True))
    _write_json(paths["intake_result"], intake.model_dump(mode="json", by_alias=True))
    result = DataCapsuleCiArtifactBridgeResult(
        decision=_bridge_decision(intake.decision),
        intake_decision=intake.decision,
        eval_leak_decision=intake.eval_leak_report.decision,
        manifest_path=request.manifest_path,
        output_dir=str(output_dir).replace("\\", "/"),
        intake_result_path=str(paths["intake_result"]).replace("\\", "/"),
        bridge_report_path=str(paths["bridge_report"]).replace("\\", "/"),
        known_limits=[
            "DataCapsule-4 converts opt-in workflow corpus manifest metadata into local review artifacts.",
            "DataCapsule-4 does not crawl directories, read private file contents, fetch URLs, call GitHub APIs, or handle tokens.",
            "A bridge pass is not rights clearance, privacy certification, data quality guarantee, evaluation-clean proof, product readiness, or action authorization.",
        ],
    )
    _write_json(paths["bridge_result"], result.model_dump(mode="json", by_alias=True))
    _write_text(paths["bridge_report"], build_bridge_report(result))
    write_next_steps(output_dir)
    return result


def run_sample() -> DataCapsuleCiArtifactBridgeResult:
    _write_text(SAMPLE_MANIFEST_PATH, SAMPLE_CSV_TEXT)
    return run_ci_artifact_bridge(
        DataCapsuleCiArtifactBridgeRequest(
            manifest_path=str(SAMPLE_MANIFEST_PATH).replace("\\", "/"),
            output_dir=str(OUTPUT_DIR),
            corpus_id="fixture.local/datacapsule4-corpus",
            name="DataCapsule-4 CI manifest fixture",
            commit_sha="local-fixture",
            branch="sample",
        )
    )


def audit_datacapsule4_action_manifest() -> dict[str, Any]:
    paths = [
        _repo_root() / ".github" / "actions" / "datacapsule-corpus-manifest-artifact" / "action.yml",
        _repo_root() / "examples" / "datacapsule_corpus_manifest_artifact_workflow.yml",
    ]
    forbidden = [
        "twine upload",
        "mcp-publisher publish",
        "git push",
        "gh release",
        "curl ",
        "wget ",
        "invoke-webrequest",
        "gh pr comment",
        "gh api",
    ]
    findings: list[str] = []
    for path in paths:
        if not path.exists():
            findings.append(f"missing:{path.relative_to(_repo_root())}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        findings.extend(f"{path.relative_to(_repo_root())}:{item}" for item in forbidden if item in text)
    active_workflow = (_repo_root() / ".github" / "workflows" / "datacapsule-corpus-manifest-artifact.yml").exists()
    result = {
        "decision": "PASS_DATACAPSULE4_ACTION_MANIFEST_SAFE" if not findings and not active_workflow else "BLOCK_DATACAPSULE4_ACTION_MANIFEST_UNSAFE",
        "manifest_exists": paths[0].exists(),
        "example_workflow_exists": paths[1].exists(),
        "active_workflow_created": active_workflow,
        "workflow_auto_enabled": False,
        "forbidden_command_findings": findings,
        "external_actions_performed": False,
        "github_api_used_by_datacapsule": False,
        "directory_crawled": False,
        "private_file_contents_read": False,
        "url_fetch_performed": False,
        "token_printed": False,
    }
    _write_json(ACTION_MANIFEST_AUDIT_PATH, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bridge opt-in CI corpus manifests into DataCapsule local artifacts.")
    parser.add_argument("--run-sample", action="store_true", help="Write and review a safe DataCapsule-4 sample.")
    parser.add_argument("--audit-manifest", action="store_true", help="Audit DataCapsule-4 action and example workflow manifests.")
    parser.add_argument("--manifest", default="", help="Local CSV, JSONL, or JSON corpus manifest.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Output directory for DataCapsule-4 artifacts.")
    parser.add_argument("--corpus-id", default="repository.local/corpus")
    parser.add_argument("--name", default="Repository local corpus manifest")
    parser.add_argument("--workflow-name", default="DataCapsule Corpus Manifest Artifact Bridge")
    parser.add_argument("--job-name", default="datacapsule-corpus-manifest")
    parser.add_argument("--commit-sha", default="")
    parser.add_argument("--branch", default="")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_manifest:
        result = audit_datacapsule4_action_manifest()
        print(f"datacapsule4_action_manifest_audit: {result['decision']}")
        return
    if args.run_sample:
        result = run_sample()
    else:
        result = run_ci_artifact_bridge(
            DataCapsuleCiArtifactBridgeRequest(
                manifest_path=args.manifest,
                output_dir=args.output_dir,
                corpus_id=args.corpus_id,
                name=args.name,
                workflow_name=args.workflow_name,
                job_name=args.job_name,
                commit_sha=args.commit_sha,
                branch=args.branch,
            )
        )
    print(f"datacapsule4_ci_artifact_bridge: {result.decision} intake={result.intake_decision}")


if __name__ == "__main__":
    main()
