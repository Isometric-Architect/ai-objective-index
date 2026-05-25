from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


OUTPUT_DIR = Path("public_launch") / "agentsec8"
EXAMPLE_WORKFLOW_PATH = Path("examples") / "agentsec8_optional_pr_review_artifact_workflow.yml"
RESULT_PATH = OUTPUT_DIR / "AGENTSEC8_OPTIONAL_WORKFLOW_RESULT.json"
WORKFLOW_AUDIT_PATH = OUTPUT_DIR / "AGENTSEC8_WORKFLOW_AUDIT.json"
CLAIM_AUDIT_PATH = OUTPUT_DIR / "AGENTSEC8_CLAIM_BOUNDARY_AUDIT.json"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "AGENTSEC8_ARTIFACT_MANIFEST.json"
OPERATOR_RUNBOOK_PATH = OUTPUT_DIR / "AGENTSEC8_OPERATOR_RUNBOOK.md"
NEXT_STEPS_PATH = OUTPUT_DIR / "AGENTSEC8_NEXT_STEPS.md"

ACTIVE_WORKFLOW_NAMES = {
    "agentsec8-optional-pr-review-artifact.yml",
    "agentsec-optional-pr-review-artifact.yml",
    "agentsec-pr-review-artifact.yml",
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
    re.compile(r"\bverified\s+tool\b", re.I),
    re.compile(r"\bsafe\s+tool\b", re.I),
    re.compile(r"\bsecurity\s+certified\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\bproduction[- ]ready\b", re.I),
    re.compile(r"\baction\s+authorized\b", re.I),
    re.compile(r"\blive\s+security\s+gateway\b", re.I),
    re.compile(r"\bautomatic\s+security\s+gateway\b", re.I),
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


def workflow_template(output_dir: str = "public_launch/agentsec8/artifacts") -> str:
    return f"""name: AgentSec Optional PR Review Artifact

on:
  workflow_dispatch:
    inputs:
      manifest_set:
        description: Path to a committed JSON manifest, JSON list, or directory of JSON MCP/tool manifests.
        required: true
        default: public_launch/agentsec2/AGENTSEC2_SAMPLE_MANIFEST_SET.json
      profile:
        description: Public-safe AgentSec policy profile.
        required: true
        default: developer_default

jobs:
  agentsec-pr-review-artifact:
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
      - name: Build AgentSec local policy artifacts
        uses: ./.github/actions/agentsec-policy-gate-artifact
        with:
          manifest-set: ${{{{ inputs.manifest_set }}}}
          output-dir: {output_dir}
          profile: ${{{{ inputs.profile }}}}
      - name: Upload AgentSec review artifacts
        uses: actions/upload-artifact@v4
        with:
          name: agentsec-review-artifacts
          path: {output_dir}
          if-no-files-found: error
"""


def operator_runbook() -> str:
    return """# AgentSec-8 Operator Runbook

AgentSec-8 provides an opt-in workflow artifact template. It is not active in this repository by default.

## How To Use

1. Review `examples/agentsec8_optional_pr_review_artifact_workflow.yml`.
2. Copy it into `.github/workflows/` only in a repository where the owner wants the workflow enabled.
3. Provide a committed MCP/tool manifest set path when manually dispatching the workflow.
4. Download the generated JSON/Markdown artifact and review HOLD/BLOCK items before use.

## Boundaries

- The template uses `workflow_dispatch`, not automatic PR posting.
- The template uploads local review artifacts; it does not post comments.
- AgentSec does not call live MCP servers, execute tools, fetch URLs, call GitHub APIs, handle tokens, certify security, guarantee quality, prove product readiness, or authorize external actions.
- Keep private thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, and commercial policy outside public artifacts.
"""


def next_steps_markdown() -> str:
    return """# AgentSec-8 Next Steps

1. Keep the workflow template in `examples/` until a repository owner explicitly opts in.
2. Consider a future gated PR-comment package only after a separate confirmation and token-safe implementation.
3. Keep AgentSec as a local metadata review layer unless a later package explicitly adds separately gated runtime proxy behavior.
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
        "agentsec-policy-gate-artifact",
    ]
    missing_markers = [marker for marker in required_markers if marker.lower() not in lowered]
    decision = (
        "PASS_AGENTSEC8_OPTIONAL_WORKFLOW_SAFE"
        if example_path.exists() and not forbidden_findings and not active_workflows and not missing_markers
        else "BLOCK_AGENTSEC8_WORKFLOW_UNSAFE"
    )
    result = {
        "schema": "AgentSec8_WorkflowAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "example_workflow_path": str(EXAMPLE_WORKFLOW_PATH).replace("\\", "/"),
        "example_workflow_exists": example_path.exists(),
        "active_workflow_created": bool(active_workflows),
        "active_workflow_findings": active_workflows,
        "workflow_auto_enabled": False,
        "forbidden_command_findings": forbidden_findings,
        "missing_required_markers": missing_markers,
        "github_api_used_by_agentsec": False,
        "pr_comment_posted": False,
        "external_actions_performed_by_agentsec": False,
        "live_mcp_called": False,
        "external_tool_executed_by_agentsec": False,
        "url_fetch_performed_by_agentsec": False,
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


def run_agentsec8_claim_audit(write_result: bool = True) -> dict[str, Any]:
    scan_paths = [
        EXAMPLE_WORKFLOW_PATH,
        Path("docs") / "agentsec8_optional_workflow_artifact.md",
        Path("docs") / "agentsec_workflow_opt_in_runbook.md",
        Path("docs") / "agentsec_workflow_artifact_limitations.md",
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
        "schema": "AgentSec8_ClaimBoundaryAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_AGENTSEC8_CLAIM_BOUNDARY" if not findings else "BLOCK_AGENTSEC8_OVERCLAIM",
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "allowed_language": [
            "opt-in workflow artifact",
            "local metadata review",
            "ALLOW/HOLD/BLOCK",
            "not verified",
            "not security certified",
            "not quality guarantee",
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
        _file_record(RESULT_PATH, "agentsec8_result"),
        _file_record(WORKFLOW_AUDIT_PATH, "workflow_audit"),
        _file_record(CLAIM_AUDIT_PATH, "claim_audit"),
        _file_record(OPERATOR_RUNBOOK_PATH, "operator_runbook"),
        _file_record(NEXT_STEPS_PATH, "next_steps"),
    ]
    missing = [record["path"] for record in records if not record["exists"]]
    result = {
        "schema": "AgentSec8_ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_AGENTSEC8_ARTIFACT_MANIFEST" if not missing else "HOLD_AGENTSEC8_ARTIFACT_MISSING",
        "artifacts": records,
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }
    _write_json(ARTIFACT_MANIFEST_PATH, result)
    return result


def build_agentsec8_optional_workflow_artifact(write_result: bool = True) -> dict[str, Any]:
    if write_result:
        _write_text(EXAMPLE_WORKFLOW_PATH, workflow_template())
        _write_text(OPERATOR_RUNBOOK_PATH, operator_runbook())
        _write_text(NEXT_STEPS_PATH, next_steps_markdown())
    workflow_audit = audit_workflow_template() if write_result else audit_workflow_template(_repo_root())
    claim_audit = run_agentsec8_claim_audit(write_result=write_result)
    agentsec7_result = _read_json(Path("public_launch") / "agentsec7" / "AGENTSEC7_BUNDLE_RESULT.json")
    decision = (
        "PASS_AGENTSEC8_OPTIONAL_WORKFLOW_ARTIFACT"
        if workflow_audit["decision"].startswith("PASS") and claim_audit["decision"].startswith("PASS")
        else "BLOCK_AGENTSEC8_OPTIONAL_WORKFLOW_ARTIFACT"
    )
    result = {
        "schema": "AgentSec8_OptionalWorkflowArtifact/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "source_package": "AgentSec-7",
        "source_decision": agentsec7_result.get("decision", "not_checked"),
        "example_workflow_path": str(EXAMPLE_WORKFLOW_PATH).replace("\\", "/"),
        "workflow_audit_path": str(WORKFLOW_AUDIT_PATH).replace("\\", "/"),
        "claim_audit_path": str(CLAIM_AUDIT_PATH).replace("\\", "/"),
        "operator_runbook_path": str(OPERATOR_RUNBOOK_PATH).replace("\\", "/"),
        "artifact_manifest_path": str(ARTIFACT_MANIFEST_PATH).replace("\\", "/"),
        "workflow_auto_enabled": False,
        "active_workflow_created": False,
        "pr_comment_posted": False,
        "github_api_used_by_agentsec": False,
        "external_actions_performed_by_agentsec": False,
        "live_mcp_called": False,
        "external_tool_executed_by_agentsec": False,
        "url_fetch_performed_by_agentsec": False,
        "network_used_by_agentsec": False,
        "token_printed": False,
        "private_kernel_exposed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
        "known_limits": [
            "opt-in workflow template only",
            "no active workflow created",
            "no automatic PR comment",
            "no GitHub API call by AgentSec",
            "no live MCP call",
            "no external tool execution by AgentSec",
            "no URL fetch by AgentSec",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not product-readiness proof",
            "not action authorization",
        ],
        "must_not_claim": [
            "do not claim verified tool status",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim live gateway protection",
            "do not claim external action authorization",
            "do not expose private kernel values",
        ],
    }
    if write_result:
        _write_json(RESULT_PATH, result)
        build_artifact_manifest()
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build AgentSec-8 optional workflow artifact templates and audits.")
    parser.add_argument("--audit-only", action="store_true", help="Audit the existing AgentSec-8 workflow template without rewriting it.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_only:
        workflow_audit = audit_workflow_template()
        claim_audit = run_agentsec8_claim_audit(write_result=True)
        print(f"agentsec8_optional_workflow_audit: {workflow_audit['decision']} claim={claim_audit['decision']}")
        return
    result = build_agentsec8_optional_workflow_artifact(write_result=not args.no_write)
    print(f"agentsec8_optional_workflow_artifact: {result['decision']}")


if __name__ == "__main__":
    main()
