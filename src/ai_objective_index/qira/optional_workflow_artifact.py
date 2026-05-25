from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


OUTPUT_DIR = Path("public_launch") / "qira9"
EXAMPLE_WORKFLOW_PATH = Path("examples") / "qira9_optional_pr_review_artifact_workflow.yml"
RESULT_PATH = OUTPUT_DIR / "QIRA9_OPTIONAL_WORKFLOW_RESULT.json"
WORKFLOW_AUDIT_PATH = OUTPUT_DIR / "QIRA9_WORKFLOW_AUDIT.json"
CLAIM_AUDIT_PATH = OUTPUT_DIR / "QIRA9_CLAIM_BOUNDARY_AUDIT.json"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "QIRA9_ARTIFACT_MANIFEST.json"
OPERATOR_RUNBOOK_PATH = OUTPUT_DIR / "QIRA9_OPERATOR_RUNBOOK.md"
NEXT_STEPS_PATH = OUTPUT_DIR / "QIRA9_NEXT_STEPS.md"

ACTIVE_WORKFLOW_NAMES = {
    "qira9-optional-pr-review-artifact.yml",
    "qira-optional-pr-review-artifact.yml",
    "qira-pr-review-artifact.yml",
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
    re.compile(r"\bverified\s+patch\b", re.I),
    re.compile(r"\bsafe\s+patch\b", re.I),
    re.compile(r"\bsecurity\s+certified\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\bproduction[- ]ready\b", re.I),
    re.compile(r"\bdeployment\s+approved\b", re.I),
    re.compile(r"\blegal\s+compliance\s+confirmed\b", re.I),
    re.compile(r"\bexternal\s+action\s+authorized\b", re.I),
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


def workflow_template(output_dir: str = "public_launch/qira9/artifacts") -> str:
    return f"""name: QIRA Optional PR Review Artifact

on:
  workflow_dispatch:
    inputs:
      packet:
        description: Path to a committed QIRA task packet JSON file.
        required: true
        default: public_launch/qira7/QIRA7_SAMPLE_TASK_PACKET.json

jobs:
  qira-pr-review-artifact:
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
      - name: Run repository-owned QIRA checks
        id: qira_checks
        continue-on-error: true
        run: python -m pytest tests/test_qira_ci_evidence.py tests/test_qira_ci_evidence_cli.py
      - name: Bridge QIRA CI evidence
        uses: ./.github/actions/qira-ci-evidence-bridge
        with:
          packet: ${{{{ inputs.packet }}}}
          output-dir: {output_dir}
          check-name: qira targeted pytest
          check-command: python -m pytest tests/test_qira_ci_evidence.py tests/test_qira_ci_evidence_cli.py
          check-status: ${{{{ steps.qira_checks.outcome == 'success' && 'pass' || 'fail' }}}}
          exit-code: ${{{{ steps.qira_checks.outcome == 'success' && '0' || '1' }}}}
          evidence-summary: Repository-owned QIRA targeted tests completed before bridge intake.
      - name: Upload QIRA review artifacts
        uses: actions/upload-artifact@v4
        with:
          name: qira-review-artifacts
          path: {output_dir}
          if-no-files-found: error
"""


def operator_runbook() -> str:
    return """# QIRA-9 Operator Runbook

QIRA-9 provides an opt-in workflow artifact template. It is not active in this repository by default.

## How To Use

1. Review `examples/qira9_optional_pr_review_artifact_workflow.yml`.
2. Copy it into `.github/workflows/` only in a repository where the owner wants the workflow enabled.
3. Provide a committed QIRA task packet path when manually dispatching the workflow.
4. Download the generated JSON/Markdown artifact and review HOLD/BLOCK items before using the related patch.

## Boundaries

- The template uses `workflow_dispatch`, not automatic PR posting.
- Repository-owned CI may run the listed checks only after a repository owner enables the template.
- QIRA does not post comments, call GitHub APIs on behalf of QIRA, apply patches, merge, deploy, upload packages, publish registry metadata, handle tokens, certify security, guarantee quality, prove product readiness, or grant authorization for external actions.
- Keep private thresholds, anti-gaming rules, private negative controls, private probe seeds, and commercial policy outside public artifacts.
"""


def next_steps_markdown() -> str:
    return """# QIRA-9 Next Steps

1. Keep the workflow template in `examples/` until a repository owner explicitly opts in.
2. Consider a future gated PR-comment package only after a separate confirmation and token-safe implementation.
3. Keep QIRA report generation separate from merge, deploy, package upload, registry publishing, and production decisions.
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
        "qira-ci-evidence-bridge",
    ]
    missing_markers = [marker for marker in required_markers if marker.lower() not in lowered]
    decision = (
        "PASS_QIRA9_OPTIONAL_WORKFLOW_SAFE"
        if example_path.exists() and not forbidden_findings and not active_workflows and not missing_markers
        else "BLOCK_QIRA9_WORKFLOW_UNSAFE"
    )
    result = {
        "schema": "QIRA9_WorkflowAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "example_workflow_path": str(EXAMPLE_WORKFLOW_PATH).replace("\\", "/"),
        "example_workflow_exists": example_path.exists(),
        "active_workflow_created": bool(active_workflows),
        "active_workflow_findings": active_workflows,
        "workflow_auto_enabled": False,
        "forbidden_command_findings": forbidden_findings,
        "missing_required_markers": missing_markers,
        "github_api_used_by_qira": False,
        "pr_comment_posted": False,
        "external_actions_performed_by_qira": False,
        "commands_executed_by_qira": False,
        "patch_applied": False,
        "merge_performed": False,
        "deploy_performed": False,
        "token_printed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
    }
    if root is None:
        _write_json(WORKFLOW_AUDIT_PATH, result)
    return result


def _safe_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in SAFE_CONTEXT_MARKERS)


def run_qira9_claim_audit(write_result: bool = True) -> dict[str, Any]:
    scan_paths = [
        EXAMPLE_WORKFLOW_PATH,
        Path("docs") / "qira9_optional_workflow_artifact.md",
        Path("docs") / "qira_workflow_opt_in_runbook.md",
        Path("docs") / "qira_workflow_artifact_limitations.md",
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
        "schema": "QIRA9_ClaimBoundaryAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_QIRA9_CLAIM_BOUNDARY" if not findings else "BLOCK_QIRA9_OVERCLAIM",
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "allowed_language": [
            "opt-in workflow artifact",
            "repository-owned CI evidence",
            "local release-gate receipt",
            "ALLOW/HOLD/BLOCK",
            "not verified",
            "not security certified",
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
        _file_record(RESULT_PATH, "qira9_result"),
        _file_record(WORKFLOW_AUDIT_PATH, "workflow_audit"),
        _file_record(CLAIM_AUDIT_PATH, "claim_audit"),
        _file_record(OPERATOR_RUNBOOK_PATH, "operator_runbook"),
        _file_record(NEXT_STEPS_PATH, "next_steps"),
    ]
    missing = [record["path"] for record in records if not record["exists"]]
    result = {
        "schema": "QIRA9_ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_QIRA9_ARTIFACT_MANIFEST" if not missing else "HOLD_QIRA9_ARTIFACT_MISSING",
        "artifacts": records,
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }
    _write_json(ARTIFACT_MANIFEST_PATH, result)
    return result


def build_qira9_optional_workflow_artifact(write_result: bool = True) -> dict[str, Any]:
    if write_result:
        _write_text(EXAMPLE_WORKFLOW_PATH, workflow_template())
        _write_text(OPERATOR_RUNBOOK_PATH, operator_runbook())
        _write_text(NEXT_STEPS_PATH, next_steps_markdown())
    workflow_audit = audit_workflow_template() if write_result else audit_workflow_template(_repo_root())
    claim_audit = run_qira9_claim_audit(write_result=write_result)
    qira8_result = _read_json(Path("public_launch") / "qira8" / "QIRA8_BUNDLE_RESULT.json")
    decision = (
        "PASS_QIRA9_OPTIONAL_WORKFLOW_ARTIFACT"
        if workflow_audit["decision"].startswith("PASS") and claim_audit["decision"].startswith("PASS")
        else "BLOCK_QIRA9_OPTIONAL_WORKFLOW_ARTIFACT"
    )
    result = {
        "schema": "QIRA9_OptionalWorkflowArtifact/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "source_package": "QIRA-8",
        "source_decision": qira8_result.get("decision", "not_checked"),
        "example_workflow_path": str(EXAMPLE_WORKFLOW_PATH).replace("\\", "/"),
        "workflow_audit_path": str(WORKFLOW_AUDIT_PATH).replace("\\", "/"),
        "claim_audit_path": str(CLAIM_AUDIT_PATH).replace("\\", "/"),
        "operator_runbook_path": str(OPERATOR_RUNBOOK_PATH).replace("\\", "/"),
        "artifact_manifest_path": str(ARTIFACT_MANIFEST_PATH).replace("\\", "/"),
        "workflow_auto_enabled": False,
        "active_workflow_created": False,
        "pr_comment_posted": False,
        "github_api_used_by_qira": False,
        "external_actions_performed_by_qira": False,
        "commands_executed_by_qira": False,
        "patch_applied": False,
        "merge_performed": False,
        "deploy_performed": False,
        "package_uploaded": False,
        "registry_published": False,
        "token_printed": False,
        "private_kernel_exposed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
        "known_limits": [
            "opt-in workflow template only",
            "no active workflow created",
            "no automatic PR comment",
            "no GitHub API call by QIRA",
            "no commands executed by QIRA",
            "no patch application",
            "no merge",
            "no deploy",
            "no package upload",
            "no registry publish",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not product-readiness proof",
            "not authorization for external actions",
        ],
        "must_not_claim": [
            "do not claim verified patch status",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim deployment approval",
            "do not claim authorization for external actions",
            "do not expose private kernel values",
        ],
    }
    if write_result:
        _write_json(RESULT_PATH, result)
        build_artifact_manifest()
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build QIRA-9 optional workflow artifact templates and audits.")
    parser.add_argument("--audit-only", action="store_true", help="Audit the existing QIRA-9 workflow template without rewriting it.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_only:
        workflow_audit = audit_workflow_template()
        claim_audit = run_qira9_claim_audit(write_result=True)
        print(f"qira9_optional_workflow_audit: {workflow_audit['decision']} claim={claim_audit['decision']}")
        return
    result = build_qira9_optional_workflow_artifact(write_result=not args.no_write)
    print(f"qira9_optional_workflow_artifact: {result['decision']}")


if __name__ == "__main__":
    main()
