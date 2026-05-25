from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .residualops_public_private_alignment_audit import run_public_private_alignment_audit


OUTPUT_DIR = Path("public_launch") / "roe4"
DISTRIBUTION_GATE_PATH = OUTPUT_DIR / "ROE4_DISTRIBUTION_SPLIT_GATE.json"
DISTRIBUTION_MATRIX_PATH = OUTPUT_DIR / "ROE4_PUBLIC_PRIVATE_DISTRIBUTION_MATRIX.json"
OPT_IN_RUNBOOK_PATH = OUTPUT_DIR / "ROE4_OPT_IN_WORKFLOW_DISTRIBUTION_RUNBOOK.md"
DISTRIBUTION_SUMMARY_PATH = OUTPUT_DIR / "ROE4_PORTFOLIO_DISTRIBUTION_SUMMARY.md"
CLAIM_AUDIT_PATH = OUTPUT_DIR / "ROE4_CLAIM_BOUNDARY_AUDIT.json"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "ROE4_ARTIFACT_MANIFEST.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "ROE4_NEXT_STEPS.md"

VERTICALS: list[dict[str, Any]] = [
    {
        "vertical_id": "qira",
        "product_name": "QIRA-Code ReleaseGate",
        "package": "QIRA-9",
        "public_surface": "opt-in workflow artifact template for local PR/release review",
        "example_workflow": "examples/qira9_optional_pr_review_artifact_workflow.yml",
        "result_path": "public_launch/qira9/QIRA9_OPTIONAL_WORKFLOW_RESULT.json",
        "workflow_audit_path": "public_launch/qira9/QIRA9_WORKFLOW_AUDIT.json",
        "claim_audit_path": "public_launch/qira9/QIRA9_CLAIM_BOUNDARY_AUDIT.json",
        "active_workflow_names": [
            "qira9-optional-pr-review-artifact.yml",
            "qira-optional-pr-review-artifact.yml",
            "qira-pr-review-artifact.yml",
        ],
    },
    {
        "vertical_id": "agentsec",
        "product_name": "AgentSec Gate",
        "package": "AgentSec-8",
        "public_surface": "opt-in workflow artifact template for local MCP/tool manifest review",
        "example_workflow": "examples/agentsec8_optional_pr_review_artifact_workflow.yml",
        "result_path": "public_launch/agentsec8/AGENTSEC8_OPTIONAL_WORKFLOW_RESULT.json",
        "workflow_audit_path": "public_launch/agentsec8/AGENTSEC8_WORKFLOW_AUDIT.json",
        "claim_audit_path": "public_launch/agentsec8/AGENTSEC8_CLAIM_BOUNDARY_AUDIT.json",
        "active_workflow_names": [
            "agentsec8-optional-pr-review-artifact.yml",
            "agentsec-optional-pr-review-artifact.yml",
            "agentsec-pr-review-artifact.yml",
        ],
    },
    {
        "vertical_id": "datacapsule",
        "product_name": "DataCapsule / AIDREG Engine",
        "package": "DataCapsule-7",
        "public_surface": "opt-in workflow artifact template for local corpus manifest review",
        "example_workflow": "examples/datacapsule7_repository_manifest_workflow.yml",
        "result_path": "public_launch/datacapsule7/DATACAPSULE7_OPTIONAL_WORKFLOW_RESULT.json",
        "workflow_audit_path": "public_launch/datacapsule7/DATACAPSULE7_WORKFLOW_AUDIT.json",
        "claim_audit_path": "public_launch/datacapsule7/DATACAPSULE7_CLAIM_BOUNDARY_AUDIT.json",
        "active_workflow_names": [
            "datacapsule7-repository-manifest-artifact.yml",
            "datacapsule-optional-repository-manifest-artifact.yml",
            "datacapsule-repository-manifest-artifact.yml",
        ],
    },
]

PUBLIC_ALLOWED = [
    "schemas and artifact shapes",
    "endpoint or workflow template shapes",
    "high-level packet, manifest, capsule, residual, receipt, and ALLOW/HOLD/BLOCK language",
    "public-safe fake fixtures and local negative-control summaries",
    "claim boundaries and limitations",
    "opt-in workflow artifact examples under examples/",
]

PRIVATE_RESERVED = [
    "private ranking calibration values",
    "threshold policy",
    "anti-gaming policy details",
    "provider trust priors",
    "private negative-control banks",
    "private probe seeds",
    "private receipt weighting",
    "commercial routing policy",
    "enterprise data policy",
    "partner-specific strategy",
]

RISKY_PATTERNS = [
    ("overclaim", re.compile(r"\bverified\s+capability\b", re.I)),
    ("overclaim", re.compile(r"\bsafe\s+tool\b", re.I)),
    ("overclaim", re.compile(r"\bsecurity\s+certified\b", re.I)),
    ("overclaim", re.compile(r"\bquality\s+guaranteed\b", re.I)),
    ("overclaim", re.compile(r"\bproduction\s+ready\b", re.I)),
    ("overclaim", re.compile(r"\blegal\s+sufficiency\s+confirmed\b", re.I)),
    ("overclaim", re.compile(r"\bprivacy\s+compliant\b", re.I)),
    ("overclaim", re.compile(r"\blicense\s+cleared\b", re.I)),
    ("overclaim", re.compile(r"\beval\s+clean\b", re.I)),
    ("overclaim", re.compile(r"\baction\s+authorized\b", re.I)),
    ("overclaim", re.compile(r"\bexternal\s+action\s+authorization\b", re.I)),
    ("private_kernel", re.compile(r"\bprivate\s+ranking\s+weights?\s*[:=]\s*\d", re.I)),
    ("private_kernel", re.compile(r"\bprovider\s+trust\s+prior\s*[:=]\s*\d", re.I)),
    ("private_kernel", re.compile(r"\banti-gaming\s+threshold\s*[:=]\s*\d", re.I)),
    ("private_kernel", re.compile(r"\bprivate\s+negative-control\s+seed\s*[:=]", re.I)),
    ("private_kernel", re.compile(r"\bcommercial\s+routing\s+policy\s*[:=]\s*\d", re.I)),
]

SAFE_CONTEXT = [
    "not ",
    "no ",
    "do not",
    "does not",
    "cannot ",
    "without ",
    "must not",
    "remain private",
    "remains private",
    "non-public",
    "private / should not be public",
    "claim boundary",
    "must_not_claim",
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any], root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _write_text(path: Path, text: str, root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _read_json(relative: str | Path, root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    path = base / relative
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_record(relative: str | Path, role: str, root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    rel = Path(relative)
    path = base / rel
    exists = path.exists() and path.is_file()
    return {
        "path": str(rel).replace("\\", "/"),
        "role": role,
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else 0,
        "sha256": _sha256(path) if exists else "",
    }


def _safe_line(line: str, previous_lines: list[str] | None = None) -> bool:
    lowered = line.lower()
    if any(marker in lowered for marker in SAFE_CONTEXT):
        return True
    context = "\n".join(previous_lines or []).lower()
    return any(
        marker in context
        for marker in [
            "forbidden public claims",
            "must not claim",
            "must_not_claim",
            "known limits",
            "private reserved",
        ]
    )


def _candidate_files(root: Path, paths: list[Path] | None = None) -> list[Path]:
    selected = paths or [
        Path("README.md"),
        Path("CHANGELOG.md"),
        Path("docs") / "roe4_public_private_distribution_split.md",
        Path("docs") / "residualops_opt_in_workflow_distribution_runbook.md",
        Path("docs") / "residualops_distribution_limitations.md",
        Path("docs") / "residualops_portfolio_handoff.md",
        OUTPUT_DIR,
    ]
    files: list[Path] = []
    for relative in selected:
        path = root / relative
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt", ".yml", ".yaml"}:
            files.append(path)
        elif path.is_dir():
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file() and child.suffix.lower() in {".md", ".json", ".txt", ".yml", ".yaml"}
            )
    return sorted(set(files))


def run_roe4_claim_audit(
    write_result: bool = True,
    root: Path | None = None,
    paths: list[Path] | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    findings: list[dict[str, Any]] = []
    for path in _candidate_files(base, paths):
        rel = str(path.relative_to(base)).replace("\\", "/")
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if _safe_line(line, lines[max(0, line_number - 6) : line_number - 1]):
                continue
            for finding_type, pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "path": rel,
                            "line": line_number,
                            "finding_type": finding_type,
                            "pattern": pattern.pattern,
                        }
                    )
                    break
    finding_types = {finding["finding_type"] for finding in findings}
    if "private_kernel" in finding_types:
        decision = "BLOCK_ROE4_PRIVATE_KERNEL_LEAK"
    elif "overclaim" in finding_types:
        decision = "BLOCK_ROE4_OVERCLAIM"
    else:
        decision = "PASS_ROE4_CLAIM_BOUNDARY"
    result = {
        "schema": "ResidualOps_ROE4ClaimBoundaryAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "finding_count": len(findings),
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
        "private_kernel_exposed": "private_kernel" in finding_types,
    }
    if write_result:
        _write_json(CLAIM_AUDIT_PATH, result, root=base)
    return result


def active_workflow_findings(root: Path | None = None) -> list[str]:
    base = root or _repo_root()
    workflow_dir = base / ".github" / "workflows"
    if not workflow_dir.exists():
        return []
    findings: list[str] = []
    for vertical in VERTICALS:
        for name in vertical["active_workflow_names"]:
            if (workflow_dir / name).exists():
                findings.append(str(Path(".github") / "workflows" / name).replace("\\", "/"))
    return sorted(set(findings))


def _decision_is_pass(payload: dict[str, Any]) -> bool:
    return str(payload.get("decision", "")).upper().startswith("PASS")


def _unsafe_flags(payload: dict[str, Any], vertical_id: str) -> list[str]:
    keys = [
        "workflow_auto_enabled",
        "active_workflow_created",
        "review_comment_posted",
        "pr_comment_posted",
        "github_api_used",
        f"github_api_used_by_{vertical_id}",
        "external_actions_performed",
        f"external_actions_performed_by_{vertical_id}",
        "crawler_used",
        "network_used",
        f"network_used_by_{vertical_id}",
        "live_mcp_called",
        "external_tool_executed",
        f"external_tool_executed_by_{vertical_id}",
        "url_fetch_performed",
        f"url_fetch_performed_by_{vertical_id}",
        "token_printed",
        "private_kernel_exposed",
        "can_authorize_action",
    ]
    return [key for key in keys if payload.get(key) is True]


def build_distribution_matrix(root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    vertical_entries: list[dict[str, Any]] = []
    missing_artifacts: list[str] = []
    unsafe_flags: list[dict[str, Any]] = []
    non_pass_decisions: list[dict[str, Any]] = []
    for vertical in VERTICALS:
        records = [
            _file_record(vertical["example_workflow"], "opt_in_example_workflow", root=base),
            _file_record(vertical["result_path"], "optional_workflow_result", root=base),
            _file_record(vertical["workflow_audit_path"], "workflow_audit", root=base),
            _file_record(vertical["claim_audit_path"], "claim_audit", root=base),
        ]
        missing_artifacts.extend(record["path"] for record in records if not record["exists"])
        result = _read_json(vertical["result_path"], root=base)
        workflow_audit = _read_json(vertical["workflow_audit_path"], root=base)
        claim_audit = _read_json(vertical["claim_audit_path"], root=base)
        for role, payload in [("result", result), ("workflow_audit", workflow_audit), ("claim_audit", claim_audit)]:
            if payload and not _decision_is_pass(payload):
                non_pass_decisions.append(
                    {
                        "vertical_id": vertical["vertical_id"],
                        "role": role,
                        "decision": payload.get("decision", "UNKNOWN"),
                    }
                )
            for flag in _unsafe_flags(payload, vertical["vertical_id"]):
                unsafe_flags.append({"vertical_id": vertical["vertical_id"], "role": role, "flag": flag})
        vertical_entries.append(
            {
                "vertical_id": vertical["vertical_id"],
                "product_name": vertical["product_name"],
                "package": vertical["package"],
                "public_surface": vertical["public_surface"],
                "example_workflow": vertical["example_workflow"],
                "primary_decision": result.get("decision", "UNKNOWN"),
                "workflow_audit_decision": workflow_audit.get("decision", "UNKNOWN"),
                "claim_audit_decision": claim_audit.get("decision", "UNKNOWN"),
                "artifacts": records,
                "public_allowed": PUBLIC_ALLOWED,
                "private_reserved": PRIVATE_RESERVED,
                "operator_mode": "repository-owner opt-in only",
            }
        )
    return {
        "schema": "ResidualOps_ROE4PublicPrivateDistributionMatrix/v0.1",
        "generated_at": _timestamp(),
        "vertical_count": len(vertical_entries),
        "verticals": vertical_entries,
        "public_allowed": PUBLIC_ALLOWED,
        "private_reserved": PRIVATE_RESERVED,
        "active_workflow_findings": active_workflow_findings(base),
        "missing_artifacts": sorted(set(missing_artifacts)),
        "non_pass_decisions": non_pass_decisions,
        "unsafe_flag_findings": unsafe_flags,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "github_api_used": False,
        "network_used": False,
        "token_printed": False,
        "private_kernel_exposed": False,
    }


def opt_in_runbook_markdown(matrix: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {name} | `{package}` | `{workflow}` | {surface} |".format(
            name=vertical["product_name"],
            package=vertical["package"],
            workflow=vertical["example_workflow"],
            surface=vertical["public_surface"],
        )
        for vertical in matrix["verticals"]
    )
    return f"""# ROE-4 Opt-In Workflow Distribution Runbook

ROE-4 describes how to distribute the current ResidualOps workflow artifact templates without enabling them automatically.

| Vertical | Package | Example Workflow | Public Surface |
| --- | --- | --- | --- |
{rows}

## Operator Sequence

1. Review the target vertical's example workflow under `examples/`.
2. Confirm the target repository owner wants the workflow enabled.
3. Copy exactly one reviewed example workflow into `.github/workflows/` in that target repository.
4. Keep the first run manual through `workflow_dispatch`.
5. Download the generated artifact and review HOLD/BLOCK rows before using any result.

## Public / Private Rule

Public artifacts may describe schemas, artifact shapes, high-level components, local fixture summaries, ALLOW/HOLD/BLOCK labels, and claim boundaries.

Private material remains non-public: exact weights, thresholds, anti-gaming rules, provider trust priors, private negative-control banks, private probe seeds, private receipt weighting, commercial routing policy, and enterprise data policy.

## Boundary

ROE-4 does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/evaluation status, provide purchasing advice, or authorize actions.
"""


def distribution_summary_markdown(gate: dict[str, Any], matrix: dict[str, Any]) -> str:
    packages = ", ".join(f"{vertical['package']}" for vertical in matrix["verticals"])
    return f"""# ROE-4 Portfolio Distribution Summary

Decision: `{gate['decision']}`

ROE-4 aligns the public distribution surface for {packages}.

The package creates a public/private distribution matrix and an opt-in workflow runbook. It keeps executable workflow enablement out of the repository and keeps private kernel details non-public.

## Current Result

- verticals: `{matrix['vertical_count']}`
- missing artifacts: `{len(matrix['missing_artifacts'])}`
- active workflow findings: `{len(matrix['active_workflow_findings'])}`
- unsafe flag findings: `{len(matrix['unsafe_flag_findings'])}`
- claim audit: `{gate['claim_audit_decision']}`
- public/private alignment: `{gate['public_private_alignment_decision']}`

## Boundary

This is distribution readiness for public-safe artifacts only. It is not verification, certification, readiness proof, legal/privacy/license/evaluation proof, purchasing advice, or authorization for actions.
"""


def next_steps_markdown(gate: dict[str, Any]) -> str:
    if gate["decision"] == "PASS_ROE4_DISTRIBUTION_SPLIT_READY":
        next_step = "ROE-5 portfolio onboarding kit or a first external repository pilot with one manually enabled workflow."
    else:
        next_step = "Fix the ROE-4 HOLD/BLOCK items before increasing distribution."
    return f"""# ROE-4 Next Steps

Decision: `{gate['decision']}`

Recommended next step: {next_step}

Do not enable workflows automatically. Do not move private kernel values into public docs, examples, or artifacts.
"""


def build_distribution_gate(
    write_result: bool = False,
    root: Path | None = None,
    matrix: dict[str, Any] | None = None,
    claim_audit: dict[str, Any] | None = None,
    alignment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    active_matrix = matrix or build_distribution_matrix(base)
    active_claim_audit = claim_audit or run_roe4_claim_audit(write_result=False, root=base)
    active_alignment = alignment or run_public_private_alignment_audit(
        write_result=False,
        root=base,
        paths=[Path("docs"), OUTPUT_DIR, Path("README.md"), Path("CHANGELOG.md")],
    )
    issues: list[str] = []
    decision = "PASS_ROE4_DISTRIBUTION_SPLIT_READY"
    if active_matrix["active_workflow_findings"]:
        decision = "BLOCK_ROE4_ACTIVE_WORKFLOW_FOUND"
        issues.append("active workflow template found under .github/workflows")
    elif active_matrix["unsafe_flag_findings"]:
        decision = "BLOCK_ROE4_UNSAFE_PUBLIC_SURFACE"
        issues.append("unsafe public-surface flags found")
    elif active_claim_audit["decision"].startswith("BLOCK"):
        decision = active_claim_audit["decision"]
        issues.append("ROE-4 claim audit failed")
    elif active_alignment["decision"].startswith("BLOCK"):
        decision = "BLOCK_ROE4_PUBLIC_PRIVATE_ALIGNMENT"
        issues.append(f"public/private alignment {active_alignment['decision']}")
    elif active_matrix["missing_artifacts"]:
        decision = "HOLD_ROE4_ARTIFACTS_MISSING"
        issues.append("required public-safe artifacts missing")
    elif active_matrix["non_pass_decisions"]:
        decision = "HOLD_ROE4_VERTICAL_SURFACE_REVIEW"
        issues.append("one or more vertical surface decisions are not PASS")
    result = {
        "schema": "ResidualOps_ROE4DistributionSplitGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "issues": issues,
        "vertical_count": active_matrix["vertical_count"],
        "matrix_path": str(DISTRIBUTION_MATRIX_PATH).replace("\\", "/"),
        "claim_audit_path": str(CLAIM_AUDIT_PATH).replace("\\", "/"),
        "claim_audit_decision": active_claim_audit["decision"],
        "public_private_alignment_decision": active_alignment["decision"],
        "missing_artifact_count": len(active_matrix["missing_artifacts"]),
        "active_workflow_findings": active_matrix["active_workflow_findings"],
        "unsafe_flag_findings": active_matrix["unsafe_flag_findings"],
        "non_pass_decisions": active_matrix["non_pass_decisions"],
        "public_allowed": PUBLIC_ALLOWED,
        "private_reserved": PRIVATE_RESERVED,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "github_api_used": False,
        "review_comment_posted": False,
        "crawler_used": False,
        "network_used": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "token_printed": False,
        "private_kernel_exposed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
    }
    if write_result:
        _write_json(DISTRIBUTION_GATE_PATH, result, root=base)
    return result


def build_artifact_manifest(root: Path | None = None) -> dict[str, Any]:
    paths = [
        DISTRIBUTION_GATE_PATH,
        DISTRIBUTION_MATRIX_PATH,
        OPT_IN_RUNBOOK_PATH,
        DISTRIBUTION_SUMMARY_PATH,
        CLAIM_AUDIT_PATH,
        NEXT_STEPS_PATH,
    ]
    records = [_file_record(path, "roe4_output", root=root) for path in paths]
    missing = [record["path"] for record in records if not record["exists"]]
    return {
        "schema": "ResidualOps_ROE4ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_ROE4_ARTIFACT_MANIFEST" if not missing else "HOLD_ROE4_ARTIFACT_MISSING",
        "artifacts": records,
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }


def run_distribution_split_gate(write_result: bool = True) -> dict[str, Any]:
    matrix = build_distribution_matrix()
    if write_result:
        _write_json(DISTRIBUTION_MATRIX_PATH, matrix)
        _write_text(OPT_IN_RUNBOOK_PATH, opt_in_runbook_markdown(matrix))
    claim_audit = run_roe4_claim_audit(write_result=write_result)
    alignment = run_public_private_alignment_audit(
        write_result=False,
        paths=[Path("docs"), OUTPUT_DIR, Path("README.md"), Path("CHANGELOG.md")],
    )
    gate = build_distribution_gate(
        write_result=write_result,
        matrix=matrix,
        claim_audit=claim_audit,
        alignment=alignment,
    )
    if write_result:
        _write_text(DISTRIBUTION_SUMMARY_PATH, distribution_summary_markdown(gate, matrix))
        _write_text(NEXT_STEPS_PATH, next_steps_markdown(gate))
        manifest = build_artifact_manifest()
        _write_json(ARTIFACT_MANIFEST_PATH, manifest)
    return gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ROE-4 public/private distribution split gate.")
    parser.add_argument("--audit-only", action="store_true", help="Run the ROE-4 claim audit only.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing public outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_only:
        result = run_roe4_claim_audit(write_result=not args.no_write)
        print(f"residualops_distribution_gate_audit: {result['decision']} findings={result['finding_count']}")
        return
    result = run_distribution_split_gate(write_result=not args.no_write)
    print(f"residualops_distribution_gate: {result['decision']} verticals={result['vertical_count']}")


if __name__ == "__main__":
    main()
