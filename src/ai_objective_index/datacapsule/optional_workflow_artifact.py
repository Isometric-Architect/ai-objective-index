from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


OUTPUT_DIR = Path("public_launch") / "datacapsule7"
EXAMPLE_WORKFLOW_PATH = Path("examples") / "datacapsule7_repository_manifest_workflow.yml"
RESULT_PATH = OUTPUT_DIR / "DATACAPSULE7_OPTIONAL_WORKFLOW_RESULT.json"
WORKFLOW_AUDIT_PATH = OUTPUT_DIR / "DATACAPSULE7_WORKFLOW_AUDIT.json"
CLAIM_AUDIT_PATH = OUTPUT_DIR / "DATACAPSULE7_CLAIM_BOUNDARY_AUDIT.json"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "DATACAPSULE7_ARTIFACT_MANIFEST.json"
OPERATOR_RUNBOOK_PATH = OUTPUT_DIR / "DATACAPSULE7_OPERATOR_RUNBOOK.md"
NEXT_STEPS_PATH = OUTPUT_DIR / "DATACAPSULE7_NEXT_STEPS.md"

ACTIVE_WORKFLOW_NAMES = {
    "datacapsule7-repository-manifest-artifact.yml",
    "datacapsule-optional-repository-manifest-artifact.yml",
    "datacapsule-repository-manifest-artifact.yml",
}

FORBIDDEN_COMMAND_PATTERNS = [
    "gh pr comment",
    "gh api",
    "git push",
    "twine upload",
    "mcp-publisher publish",
    "curl ",
    "wget ",
    "invoke-webrequest",
    "powershell -encodedcommand",
]

RISKY_CLAIM_PATTERNS = [
    re.compile(r"\blegal\s+sufficiency\s+confirmed\b", re.I),
    re.compile(r"\bprivacy\s+compliant\b", re.I),
    re.compile(r"\blicense\s+cleared\b", re.I),
    re.compile(r"\bdata\s+quality\s+guaranteed\b", re.I),
    re.compile(r"\bevaluation\s+cleanliness\s+proved\b", re.I),
    re.compile(r"\beval\s+clean\b", re.I),
    re.compile(r"\bpurchase\s+recommended\b", re.I),
    re.compile(r"\baction\s+authorized\b", re.I),
]

SAFE_CONTEXT_MARKERS = [
    "not ",
    "no ",
    "must not",
    "do not",
    "does not",
    "without claiming",
    "claim boundary",
    "must_not_claim",
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: Path) -> dict[str, Any]:
    full_path = _repo_root() / path
    if not full_path.exists():
        return {}
    try:
        payload = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _file_record(relative: Path, role: str) -> dict[str, Any]:
    path = _repo_root() / relative
    exists = path.exists() and path.is_file()
    payload = path.read_bytes() if exists else b""
    return {
        "path": str(relative).replace("\\", "/"),
        "role": role,
        "exists": exists,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest() if exists else "",
    }


def workflow_template(output_dir: str = "public_launch/datacapsule7/artifacts") -> str:
    return f"""name: DataCapsule Optional Repository Manifest Artifact

on:
  workflow_dispatch:
    inputs:
      manifest:
        description: Path to a committed CSV, JSONL, or JSON corpus manifest.
        required: true
        default: public_launch/datacapsule3/DATACAPSULE3_SAMPLE_MANIFEST.csv
      corpus_id:
        description: Stable local corpus identifier.
        required: true
        default: repository.local/corpus
      name:
        description: Human-readable corpus name.
        required: true
        default: Repository local corpus manifest

jobs:
  datacapsule-repository-manifest-artifact:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install AOI package locally
        run: python -m pip install -e .
      - name: Build DataCapsule local corpus artifacts
        uses: ./.github/actions/datacapsule-corpus-manifest-artifact
        with:
          manifest: ${{{{ inputs.manifest }}}}
          output-dir: {output_dir}
          corpus-id: ${{{{ inputs.corpus_id }}}}
          name: ${{{{ inputs.name }}}}
      - name: Upload DataCapsule review artifacts
        uses: actions/upload-artifact@v4
        with:
          name: datacapsule-review-artifacts
          path: {output_dir}
          if-no-files-found: error
"""


def operator_runbook() -> str:
    return """# DataCapsule-7 Operator Runbook

DataCapsule-7 provides an opt-in workflow artifact template. It is not active in this repository by default.

## How To Use

1. Review `examples/datacapsule7_repository_manifest_workflow.yml`.
2. Copy it into `.github/workflows/` only in a repository where the owner wants the workflow enabled.
3. Provide a committed CSV, JSONL, or JSON corpus manifest path when manually dispatching the workflow.
4. Download the generated JSON/Markdown artifact and review HOLD/BLOCK items before using the related corpus.

## Boundaries

- The template uses `workflow_dispatch`, not automatic PR posting.
- The template uploads local review artifacts; it does not post comments.
- DataCapsule does not crawl directories, inspect private file contents, fetch URLs, call GitHub APIs, call external services, handle tokens, prove rights, certify privacy, guarantee data quality, prove evaluation cleanliness, clear licenses, provide purchasing advice, or authorize actions.
- Keep private rights analysis, receipt weighting, private negative-control banks, private probe seeds, commercial data policy, and enterprise data policy outside public artifacts.
"""


def next_steps_markdown() -> str:
    return """# DataCapsule-7 Next Steps

1. Keep the workflow template in `examples/` until a repository owner explicitly opts in.
2. Consider a future gated review-comment package only after a separate confirmation and token-safe implementation.
3. Keep DataCapsule report generation separate from crawling, private data inspection, legal review, privacy certification, license clearance, purchasing advice, and authorization for actions.
4. Continue preserving private kernel details outside public repository artifacts.
"""


def _active_workflow_findings(root: Path | None = None) -> list[str]:
    base = root or _repo_root()
    workflow_dir = base / ".github" / "workflows"
    if not workflow_dir.exists():
        return []
    findings = []
    for name in ACTIVE_WORKFLOW_NAMES:
        if (workflow_dir / name).exists():
            findings.append(str(Path(".github") / "workflows" / name).replace("\\", "/"))
    return sorted(findings)


def audit_workflow_template(root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    example_path = base / EXAMPLE_WORKFLOW_PATH
    text = example_path.read_text(encoding="utf-8", errors="ignore") if example_path.exists() else ""
    lowered = text.lower()
    forbidden_findings = [pattern for pattern in FORBIDDEN_COMMAND_PATTERNS if pattern in lowered]
    active_workflows = _active_workflow_findings(base)
    required_markers = [
        "workflow_dispatch",
        "permissions:",
        "contents: read",
        "actions/upload-artifact@v4",
        "datacapsule-corpus-manifest-artifact",
    ]
    missing_markers = [marker for marker in required_markers if marker.lower() not in lowered]
    decision = (
        "PASS_DATACAPSULE7_OPTIONAL_WORKFLOW_SAFE"
        if example_path.exists() and not forbidden_findings and not active_workflows and not missing_markers
        else "BLOCK_DATACAPSULE7_WORKFLOW_UNSAFE"
    )
    result = {
        "schema": "DataCapsule7_WorkflowAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "example_workflow_path": str(EXAMPLE_WORKFLOW_PATH).replace("\\", "/"),
        "example_workflow_exists": example_path.exists(),
        "active_workflow_created": bool(active_workflows),
        "active_workflow_findings": active_workflows,
        "workflow_auto_enabled": False,
        "forbidden_command_findings": forbidden_findings,
        "missing_required_markers": missing_markers,
        "github_api_used_by_datacapsule": False,
        "review_comment_posted": False,
        "external_actions_performed_by_datacapsule": False,
        "crawler_used": False,
        "private_file_content_read": False,
        "url_fetch_performed_by_datacapsule": False,
        "external_service_used": False,
        "token_printed": False,
        "can_certify_legal": False,
        "can_certify_privacy": False,
        "can_certify_quality": False,
        "can_clear_license": False,
        "can_prove_eval_cleanliness": False,
        "can_authorize_action": False,
    }
    if root is None:
        _write_json(WORKFLOW_AUDIT_PATH, result)
    return result


def _safe_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in SAFE_CONTEXT_MARKERS)


def run_datacapsule7_claim_audit(write_result: bool = True) -> dict[str, Any]:
    scan_paths = [
        EXAMPLE_WORKFLOW_PATH,
        Path("docs") / "datacapsule7_optional_workflow_artifact.md",
        Path("docs") / "datacapsule_workflow_opt_in_runbook.md",
        Path("docs") / "datacapsule_workflow_artifact_limitations.md",
        OUTPUT_DIR,
    ]
    findings: list[dict[str, Any]] = []
    for relative in scan_paths:
        path = _repo_root() / relative
        if not path.exists():
            continue
        files = [path] if path.is_file() else [child for child in path.rglob("*") if child.suffix.lower() in {".md", ".json", ".yml", ".yaml"}]
        for file_path in files:
            rel = str(file_path.relative_to(_repo_root())).replace("\\", "/")
            for line_number, line in enumerate(file_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                if _safe_line(line):
                    continue
                for pattern in RISKY_CLAIM_PATTERNS:
                    if pattern.search(line):
                        findings.append({"path": rel, "line": line_number, "pattern": pattern.pattern})
    result = {
        "schema": "DataCapsule7_ClaimBoundaryAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_DATACAPSULE7_CLAIM_BOUNDARY" if not findings else "BLOCK_DATACAPSULE7_OVERCLAIM",
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "allowed_language": [
            "opt-in workflow artifact",
            "local corpus metadata review",
            "source and rights review",
            "ALLOW/HOLD/BLOCK",
            "not legal sufficiency",
            "not privacy compliance",
            "not data quality guarantee",
        ],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "token_printed": False,
        "private_kernel_exposed": False,
    }
    if write_result:
        _write_json(CLAIM_AUDIT_PATH, result)
    return result


def build_artifact_manifest() -> dict[str, Any]:
    records = [
        _file_record(EXAMPLE_WORKFLOW_PATH, "opt_in_example_workflow"),
        _file_record(RESULT_PATH, "datacapsule7_result"),
        _file_record(WORKFLOW_AUDIT_PATH, "workflow_audit"),
        _file_record(CLAIM_AUDIT_PATH, "claim_audit"),
        _file_record(OPERATOR_RUNBOOK_PATH, "operator_runbook"),
        _file_record(NEXT_STEPS_PATH, "next_steps"),
    ]
    missing = [record["path"] for record in records if not record["exists"]]
    result = {
        "schema": "DataCapsule7_ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_DATACAPSULE7_ARTIFACT_MANIFEST" if not missing else "HOLD_DATACAPSULE7_ARTIFACT_MISSING",
        "artifacts": records,
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }
    _write_json(ARTIFACT_MANIFEST_PATH, result)
    return result


def build_datacapsule7_optional_workflow_artifact(write_result: bool = True) -> dict[str, Any]:
    if write_result:
        _write_text(EXAMPLE_WORKFLOW_PATH, workflow_template())
        _write_text(OPERATOR_RUNBOOK_PATH, operator_runbook())
        _write_text(NEXT_STEPS_PATH, next_steps_markdown())
    workflow_audit = audit_workflow_template() if write_result else audit_workflow_template(_repo_root())
    claim_audit = run_datacapsule7_claim_audit(write_result=write_result)
    datacapsule6_result = _read_json(Path("public_launch") / "datacapsule6" / "DATACAPSULE6_BUNDLE_RESULT.json")
    decision = (
        "PASS_DATACAPSULE7_OPTIONAL_WORKFLOW_ARTIFACT"
        if workflow_audit["decision"].startswith("PASS") and claim_audit["decision"].startswith("PASS")
        else "BLOCK_DATACAPSULE7_OPTIONAL_WORKFLOW_ARTIFACT"
    )
    result = {
        "schema": "DataCapsule7_OptionalWorkflowArtifact/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "source_package": "DataCapsule-6",
        "source_decision": datacapsule6_result.get("decision", "not_checked"),
        "example_workflow_path": str(EXAMPLE_WORKFLOW_PATH).replace("\\", "/"),
        "workflow_audit_path": str(WORKFLOW_AUDIT_PATH).replace("\\", "/"),
        "claim_audit_path": str(CLAIM_AUDIT_PATH).replace("\\", "/"),
        "operator_runbook_path": str(OPERATOR_RUNBOOK_PATH).replace("\\", "/"),
        "artifact_manifest_path": str(ARTIFACT_MANIFEST_PATH).replace("\\", "/"),
        "workflow_auto_enabled": False,
        "active_workflow_created": False,
        "review_comment_posted": False,
        "github_api_used_by_datacapsule": False,
        "external_actions_performed_by_datacapsule": False,
        "crawler_used": False,
        "private_file_content_read": False,
        "url_fetch_performed_by_datacapsule": False,
        "external_service_used": False,
        "network_used_by_datacapsule": False,
        "token_printed": False,
        "private_kernel_exposed": False,
        "can_certify_legal": False,
        "can_certify_privacy": False,
        "can_certify_quality": False,
        "can_clear_license": False,
        "can_prove_eval_cleanliness": False,
        "can_authorize_action": False,
        "known_limits": [
            "opt-in workflow template only",
            "no active workflow created",
            "no automatic review comment",
            "no GitHub API call by DataCapsule",
            "no crawling",
            "no private file-content inspection",
            "no URL fetch by DataCapsule",
            "no external service call",
            "not legal sufficiency",
            "not privacy certification",
            "not data quality guarantee",
            "not license clearance",
            "not evaluation-clean proof",
            "not purchasing advice",
            "not authorization for actions",
        ],
        "must_not_claim": [
            "do not claim legal sufficiency",
            "do not claim privacy compliance",
            "do not claim data quality guarantee",
            "do not claim license clearance",
            "do not claim evaluation cleanliness",
            "do not claim purchasing advice",
            "do not claim authorization for actions",
            "do not expose private kernel values",
        ],
    }
    if write_result:
        _write_json(RESULT_PATH, result)
        build_artifact_manifest()
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build DataCapsule-7 optional workflow artifact templates and audits.")
    parser.add_argument("--audit-only", action="store_true", help="Audit the existing DataCapsule-7 workflow template without rewriting it.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_only:
        workflow_audit = audit_workflow_template()
        claim_audit = run_datacapsule7_claim_audit(write_result=True)
        print(f"datacapsule7_optional_workflow_audit: {workflow_audit['decision']} claim={claim_audit['decision']}")
        return
    result = build_datacapsule7_optional_workflow_artifact(write_result=not args.no_write)
    print(f"datacapsule7_optional_workflow_artifact: {result['decision']}")


if __name__ == "__main__":
    main()
