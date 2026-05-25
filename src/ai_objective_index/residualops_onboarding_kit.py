from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .residualops_distribution_gate import (
    PRIVATE_RESERVED,
    PUBLIC_ALLOWED,
    VERTICALS,
    _read_json,
    run_roe4_claim_audit,
)
from .residualops_public_private_alignment_audit import run_public_private_alignment_audit


OUTPUT_DIR = Path("public_launch") / "roe5"
ONBOARDING_KIT_PATH = OUTPUT_DIR / "ROE5_PORTFOLIO_ONBOARDING_KIT.json"
SELECTION_MATRIX_PATH = OUTPUT_DIR / "ROE5_VERTICAL_SELECTION_MATRIX.json"
OWNER_CONSENT_GATE_PATH = OUTPUT_DIR / "ROE5_OWNER_CONSENT_GATE.json"
PILOT_CHECKLIST_PATH = OUTPUT_DIR / "ROE5_REPOSITORY_PILOT_CHECKLIST.md"
DRY_RUN_PLAN_PATH = OUTPUT_DIR / "ROE5_DRY_RUN_ONBOARDING_PLAN.md"
CLAIM_AUDIT_PATH = OUTPUT_DIR / "ROE5_CLAIM_BOUNDARY_AUDIT.json"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "ROE5_ARTIFACT_MANIFEST.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "ROE5_NEXT_STEPS.md"

ROE4_GATE_PATH = Path("public_launch") / "roe4" / "ROE4_DISTRIBUTION_SPLIT_GATE.json"

RECOMMENDED_FIRST_PILOT = "agentsec"

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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_record(relative: Path, role: str, root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    path = base / relative
    exists = path.exists() and path.is_file()
    return {
        "path": str(relative).replace("\\", "/"),
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
        Path("docs") / "roe5_portfolio_onboarding_kit.md",
        Path("docs") / "residualops_external_pilot_runbook.md",
        Path("docs") / "residualops_owner_consent_gate.md",
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


def run_roe5_claim_audit(
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
        decision = "BLOCK_ROE5_PRIVATE_KERNEL_LEAK"
    elif "overclaim" in finding_types:
        decision = "BLOCK_ROE5_OVERCLAIM"
    else:
        decision = "PASS_ROE5_CLAIM_BOUNDARY"
    result = {
        "schema": "ResidualOps_ROE5ClaimBoundaryAudit/v0.1",
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


def _vertical_pilot_notes(vertical_id: str) -> dict[str, Any]:
    if vertical_id == "agentsec":
        return {
            "pilot_rank": 1,
            "pilot_fit": "best first external security-facing pilot if repository has MCP/tool manifests",
            "required_inputs": ["committed MCP/tool manifest JSON or manifest set"],
            "first_run_goal": "produce local HOLD/BLOCK review artifacts without live MCP calls",
        }
    if vertical_id == "qira":
        return {
            "pilot_rank": 2,
            "pilot_fit": "fastest developer workflow pilot if repository has stable tests and PR packets",
            "required_inputs": ["committed QIRA task packet JSON", "repository-owned CI result metadata"],
            "first_run_goal": "produce local release-gate artifacts without applying patches or deploying",
        }
    return {
        "pilot_rank": 3,
        "pilot_fit": "best data governance pilot if repository has corpus manifests",
        "required_inputs": ["committed CSV, JSONL, or JSON corpus manifest"],
        "first_run_goal": "produce local data-use review artifacts without crawling or private file inspection",
    }


def build_vertical_selection_matrix(root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    verticals = []
    missing_artifacts: list[str] = []
    for vertical in VERTICALS:
        notes = _vertical_pilot_notes(vertical["vertical_id"])
        result = _read_json(vertical["result_path"], root=base)
        workflow_audit = _read_json(vertical["workflow_audit_path"], root=base)
        claim_audit = _read_json(vertical["claim_audit_path"], root=base)
        for path in [vertical["example_workflow"], vertical["result_path"], vertical["workflow_audit_path"], vertical["claim_audit_path"]]:
            if not (base / path).exists():
                missing_artifacts.append(path)
        verticals.append(
            {
                "vertical_id": vertical["vertical_id"],
                "product_name": vertical["product_name"],
                "package": vertical["package"],
                "example_workflow": vertical["example_workflow"],
                "recommended_first_pilot": vertical["vertical_id"] == RECOMMENDED_FIRST_PILOT,
                "pilot_rank": notes["pilot_rank"],
                "pilot_fit": notes["pilot_fit"],
                "required_inputs": notes["required_inputs"],
                "first_run_goal": notes["first_run_goal"],
                "result_decision": result.get("decision", "UNKNOWN"),
                "workflow_audit_decision": workflow_audit.get("decision", "UNKNOWN"),
                "claim_audit_decision": claim_audit.get("decision", "UNKNOWN"),
            }
        )
    verticals.sort(key=lambda item: item["pilot_rank"])
    decision = "PASS_ROE5_VERTICAL_SELECTION_READY" if not missing_artifacts else "HOLD_ROE5_VERTICAL_ARTIFACTS_MISSING"
    return {
        "schema": "ResidualOps_ROE5VerticalSelectionMatrix/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "recommended_first_pilot": RECOMMENDED_FIRST_PILOT,
        "verticals": verticals,
        "missing_artifacts": sorted(set(missing_artifacts)),
        "selection_rule": "Choose exactly one manually enabled workflow for the first external repository pilot.",
        "external_actions_performed": False,
        "workflow_enabled": False,
        "github_api_used": False,
        "token_printed": False,
    }


def build_owner_consent_gate(consent_present: bool = False, consent_source: str = "") -> dict[str, Any]:
    decision = "PASS_OWNER_CONSENT_RECORDED_FOR_DRY_RUN_ONLY" if consent_present else "HOLD_OWNER_CONSENT_REQUIRED_BEFORE_ENABLEMENT"
    return {
        "schema": "ResidualOps_ROE5OwnerConsentGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "owner_consent_required": True,
        "owner_consent_present": consent_present,
        "consent_source": consent_source,
        "allowed_next_action_if_missing": "prepare local onboarding artifacts only",
        "must_not_do_without_consent": [
            "do not copy workflow into .github/workflows of a target repository",
            "do not run GitHub APIs",
            "do not post comments",
            "do not request or store tokens",
            "do not enable automatic triggers",
        ],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "github_api_used": False,
        "token_printed": False,
        "can_authorize_action": False,
    }


def repository_pilot_checklist_markdown(matrix: dict[str, Any], owner_gate: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {rank} | {name} | `{package}` | `{workflow}` | {fit} |".format(
            rank=vertical["pilot_rank"],
            name=vertical["product_name"],
            package=vertical["package"],
            workflow=vertical["example_workflow"],
            fit=vertical["pilot_fit"],
        )
        for vertical in matrix["verticals"]
    )
    return f"""# ROE-5 Repository Pilot Checklist

Owner consent gate: `{owner_gate['decision']}`

Use this checklist before enabling any ResidualOps workflow in an external or separate repository.

| Rank | Vertical | Package | Example Workflow | Fit |
| --- | --- | --- | --- | --- |
{rows}

## Consent

- Confirm the repository owner wants exactly one workflow enabled for the first pilot.
- Keep first runs manual through `workflow_dispatch`.
- Do not paste tokens into chat, docs, issue text, workflow files, or manifests.

## Repository Inputs

- AgentSec: committed MCP/tool manifest JSON or manifest set.
- QIRA: committed QIRA task packet and repository-owned CI evidence metadata.
- DataCapsule: committed CSV, JSONL, or JSON corpus manifest.

## Review

- Download the generated artifact.
- Review HOLD/BLOCK findings before using any result.
- Treat the artifact as a local review aid, not as verification, certification, product-readiness proof, legal/privacy/license/evaluation proof, purchasing advice, or authorization for actions.
"""


def dry_run_onboarding_plan_markdown(matrix: dict[str, Any]) -> str:
    selected = next(item for item in matrix["verticals"] if item["recommended_first_pilot"])
    return f"""# ROE-5 Dry-Run Onboarding Plan

Recommended first pilot: `{selected['product_name']}` (`{selected['package']}`)

Reason: {selected['pilot_fit']}

## Dry Run Steps

1. Review `{selected['example_workflow']}`.
2. Confirm repository owner consent before copying any workflow.
3. Prepare the required input: {', '.join(selected['required_inputs'])}.
4. Keep the first run manual.
5. Download the workflow artifact.
6. Record HOLD/BLOCK findings and decide whether a second run is useful.

## Boundaries

This plan does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/evaluation status, provide purchasing advice, or authorize actions.
"""


def build_onboarding_kit(
    matrix: dict[str, Any] | None = None,
    owner_gate: dict[str, Any] | None = None,
    claim_audit: dict[str, Any] | None = None,
    alignment: dict[str, Any] | None = None,
    roe4_gate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_matrix = matrix or build_vertical_selection_matrix()
    active_owner_gate = owner_gate or build_owner_consent_gate()
    active_claim_audit = claim_audit or run_roe5_claim_audit(write_result=False)
    active_alignment = alignment or run_public_private_alignment_audit(
        write_result=False,
        paths=[Path("docs"), OUTPUT_DIR, Path("README.md"), Path("CHANGELOG.md")],
    )
    active_roe4_gate = roe4_gate or _read_json(ROE4_GATE_PATH)
    issues: list[str] = []
    decision = "PASS_ROE5_PORTFOLIO_ONBOARDING_KIT"
    if active_roe4_gate.get("decision") != "PASS_ROE4_DISTRIBUTION_SPLIT_READY":
        decision = "HOLD_ROE4_DISTRIBUTION_GATE_REQUIRED"
        issues.append("ROE-4 distribution gate is not PASS")
    elif active_matrix["decision"].startswith("HOLD"):
        decision = "HOLD_ROE5_VERTICAL_SELECTION_INCOMPLETE"
        issues.append("vertical selection matrix has missing artifacts")
    elif active_claim_audit["decision"].startswith("BLOCK"):
        decision = active_claim_audit["decision"]
        issues.append("ROE-5 claim audit failed")
    elif active_alignment["decision"].startswith("BLOCK"):
        decision = "BLOCK_ROE5_PUBLIC_PRIVATE_ALIGNMENT"
        issues.append(f"public/private alignment {active_alignment['decision']}")
    return {
        "schema": "ResidualOps_ROE5PortfolioOnboardingKit/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "issues": issues,
        "roe4_gate_decision": active_roe4_gate.get("decision", "UNKNOWN"),
        "vertical_selection_decision": active_matrix["decision"],
        "owner_consent_gate_decision": active_owner_gate["decision"],
        "claim_audit_decision": active_claim_audit["decision"],
        "public_private_alignment_decision": active_alignment["decision"],
        "recommended_first_pilot": active_matrix["recommended_first_pilot"],
        "owner_consent_blocks_enablement": active_owner_gate["decision"].startswith("HOLD"),
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


def next_steps_markdown(kit: dict[str, Any]) -> str:
    if kit["decision"] == "PASS_ROE5_PORTFOLIO_ONBOARDING_KIT":
        next_step = "Prepare a single-repository pilot by selecting exactly one workflow and recording owner consent outside the public repo."
    else:
        next_step = "Resolve ROE-5 HOLD/BLOCK items before any pilot."
    return f"""# ROE-5 Next Steps

Decision: `{kit['decision']}`

Recommended next step: {next_step}

Do not enable workflows automatically. Do not commit consent records containing private account data, tokens, or partner-specific strategy.
"""


def build_artifact_manifest(root: Path | None = None) -> dict[str, Any]:
    paths = [
        ONBOARDING_KIT_PATH,
        SELECTION_MATRIX_PATH,
        OWNER_CONSENT_GATE_PATH,
        PILOT_CHECKLIST_PATH,
        DRY_RUN_PLAN_PATH,
        CLAIM_AUDIT_PATH,
        NEXT_STEPS_PATH,
    ]
    records = [_file_record(path, "roe5_output", root=root) for path in paths]
    missing = [record["path"] for record in records if not record["exists"]]
    return {
        "schema": "ResidualOps_ROE5ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_ROE5_ARTIFACT_MANIFEST" if not missing else "HOLD_ROE5_ARTIFACT_MISSING",
        "artifacts": records,
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }


def run_portfolio_onboarding_kit(write_result: bool = True) -> dict[str, Any]:
    matrix = build_vertical_selection_matrix()
    owner_gate = build_owner_consent_gate()
    if write_result:
        _write_json(SELECTION_MATRIX_PATH, matrix)
        _write_json(OWNER_CONSENT_GATE_PATH, owner_gate)
        _write_text(PILOT_CHECKLIST_PATH, repository_pilot_checklist_markdown(matrix, owner_gate))
        _write_text(DRY_RUN_PLAN_PATH, dry_run_onboarding_plan_markdown(matrix))
    claim_audit = run_roe5_claim_audit(write_result=write_result)
    alignment = run_public_private_alignment_audit(
        write_result=False,
        paths=[Path("docs"), OUTPUT_DIR, Path("README.md"), Path("CHANGELOG.md")],
    )
    kit = build_onboarding_kit(matrix=matrix, owner_gate=owner_gate, claim_audit=claim_audit, alignment=alignment)
    if write_result:
        _write_json(ONBOARDING_KIT_PATH, kit)
        _write_text(NEXT_STEPS_PATH, next_steps_markdown(kit))
        _write_json(ARTIFACT_MANIFEST_PATH, build_artifact_manifest())
    return kit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the ROE-5 ResidualOps portfolio onboarding kit.")
    parser.add_argument("--audit-only", action="store_true", help="Run the ROE-5 claim audit only.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing public outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_only:
        result = run_roe5_claim_audit(write_result=not args.no_write)
        print(f"residualops_onboarding_claim_audit: {result['decision']} findings={result['finding_count']}")
        return
    result = run_portfolio_onboarding_kit(write_result=not args.no_write)
    print(f"residualops_onboarding_kit: {result['decision']} recommended_first_pilot={result['recommended_first_pilot']}")


if __name__ == "__main__":
    main()
