from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .residualops_public_private_alignment_audit import run_public_private_alignment_audit


OUTPUT_DIR = Path("public_launch") / "roe1"
INVENTORY_PATH = OUTPUT_DIR / "ROE1_VERTICAL_SURFACE_INVENTORY.json"
GATE_PATH = OUTPUT_DIR / "ROE1_SURFACE_ALIGNMENT_GATE.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE1_SUMMARY.md"
NEXT_STEPS_PATH = OUTPUT_DIR / "ROE1_NEXT_STEPS.md"


VERTICALS: list[dict[str, Any]] = [
    {
        "vertical_id": "qira",
        "product_name": "QIRA-Code ReleaseGate",
        "public_role": "AI-generated code and patch release-gate review using local packets, receipts, and artifact bundles.",
        "packages": ["QIRA-1", "QIRA-2", "QIRA-3", "QIRA-4", "QIRA-5", "QIRA-6", "QIRA-7", "QIRA-8"],
        "source_paths": [
            "src/ai_objective_index/qira/models.py",
            "src/ai_objective_index/qira/releasegate.py",
            "src/ai_objective_index/qira/reviewer_report.py",
            "src/ai_objective_index/qira/ci_evidence_bridge.py",
        ],
        "docs": [
            "docs/qira_code_releasegate_plan.md",
            "docs/qira_releasegate_mvp.md",
            "docs/qira8_pr_artifact_bundle.md",
        ],
        "actions": [
            ".github/actions/qira-releasegate-dry-run/action.yml",
            ".github/actions/qira-ci-evidence-bridge/action.yml",
        ],
        "examples": [
            "examples/qira_releasegate_dry_run_workflow.yml",
            "examples/qira_ci_evidence_bridge_workflow.yml",
        ],
        "public_outputs": ["public_launch/qira8"],
        "expected_primitives": [
            "behavior contract",
            "patch receipt",
            "residual ledger",
            "release gate report",
            "artifact bridge",
            "claim boundary",
        ],
    },
    {
        "vertical_id": "agentsec",
        "product_name": "AgentSec Gate",
        "public_role": "Local MCP/tool manifest risk review with policy-gate artifacts and explicit action boundaries.",
        "packages": ["AgentSec-1", "AgentSec-2", "AgentSec-3"],
        "source_paths": [
            "src/ai_objective_index/agentsec/models.py",
            "src/ai_objective_index/agentsec/manifest_scanner.py",
            "src/ai_objective_index/agentsec/policy_gate.py",
            "src/ai_objective_index/agentsec/ci_artifact_bridge.py",
        ],
        "docs": [
            "docs/agentsec_gate_plan.md",
            "docs/agentsec_policy_profiles.md",
            "docs/agentsec3_ci_artifact_bridge.md",
        ],
        "actions": [".github/actions/agentsec-policy-gate-artifact/action.yml"],
        "examples": ["examples/agentsec_policy_gate_artifact_workflow.yml"],
        "public_outputs": ["public_launch/agentsec3"],
        "expected_primitives": [
            "tool risk packet",
            "manifest scanner",
            "policy gate",
            "artifact bridge",
            "ALLOW/HOLD/BLOCK",
            "claim boundary",
        ],
    },
    {
        "vertical_id": "datacapsule",
        "product_name": "DataCapsule / AIDREG Engine",
        "public_role": "Local data-use boundary capsules over repository-supplied corpus manifests and eval-separation signals.",
        "packages": ["DataCapsule-1", "DataCapsule-2", "DataCapsule-3", "DataCapsule-4"],
        "source_paths": [
            "src/ai_objective_index/datacapsule/models.py",
            "src/ai_objective_index/datacapsule/capsule_builder.py",
            "src/ai_objective_index/datacapsule/manifest_intake.py",
            "src/ai_objective_index/datacapsule/ci_artifact_bridge.py",
        ],
        "docs": [
            "docs/datacapsule_engine_plan.md",
            "docs/datacapsule3_manifest_intake.md",
            "docs/datacapsule4_ci_artifact_bridge.md",
        ],
        "actions": [".github/actions/datacapsule-corpus-manifest-artifact/action.yml"],
        "examples": ["examples/datacapsule_corpus_manifest_artifact_workflow.yml"],
        "public_outputs": ["public_launch/datacapsule4"],
        "expected_primitives": [
            "corpus manifest",
            "data-use capsule",
            "use boundary",
            "negative controls",
            "eval separation report",
            "artifact bridge",
            "claim boundary",
        ],
    },
]

ACTIVE_WORKFLOW_NAMES = {
    "qira-releasegate-dry-run.yml",
    "qira-ci-evidence-bridge.yml",
    "agentsec-policy-gate-artifact.yml",
    "datacapsule-corpus-manifest-artifact.yml",
}


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


def _path_status(root: Path, paths: list[str]) -> list[dict[str, Any]]:
    statuses = []
    for relative in paths:
        path = root / relative
        statuses.append(
            {
                "path": relative,
                "exists": path.exists(),
                "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
            }
        )
    return statuses


def _active_workflow_findings(root: Path) -> list[str]:
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        return []
    findings: list[str] = []
    for child in workflows_dir.iterdir():
        if child.is_file() and child.name in ACTIVE_WORKFLOW_NAMES:
            findings.append(str(child.relative_to(root)).replace("\\", "/"))
    return sorted(findings)


def build_vertical_surface_inventory(
    root: Path | None = None,
    verticals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    selected_verticals = verticals or VERTICALS
    surfaces: list[dict[str, Any]] = []
    missing_paths: list[str] = []
    for vertical in selected_verticals:
        grouped_paths = {
            "source_paths": _path_status(base, vertical["source_paths"]),
            "docs": _path_status(base, vertical["docs"]),
            "actions": _path_status(base, vertical["actions"]),
            "examples": _path_status(base, vertical["examples"]),
            "public_outputs": _path_status(base, vertical["public_outputs"]),
        }
        for group in grouped_paths.values():
            missing_paths.extend(item["path"] for item in group if not item["exists"])
        surfaces.append(
            {
                "vertical_id": vertical["vertical_id"],
                "product_name": vertical["product_name"],
                "public_role": vertical["public_role"],
                "packages": vertical["packages"],
                "expected_primitives": vertical["expected_primitives"],
                "surface_paths": grouped_paths,
            }
        )
    active_workflows = _active_workflow_findings(base)
    if active_workflows:
        decision = "BLOCK_ACTIVE_WORKFLOW_CREATED"
    elif missing_paths:
        decision = "HOLD_VERTICAL_SURFACE_MISSING"
    else:
        decision = "PASS_VERTICAL_SURFACES_PRESENT"
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "vertical_count": len(surfaces),
        "surfaces": surfaces,
        "missing_paths": sorted(set(missing_paths)),
        "active_workflow_findings": active_workflows,
        "common_public_pattern": [
            "Packet or manifest intake",
            "Local check/probe/review",
            "Receipt or result artifact",
            "ALLOW/HOLD/BLOCK route decision",
            "Opt-in artifact bridge",
            "Claim boundary",
        ],
        "external_actions_performed": False,
        "network_used": False,
        "token_printed": False,
        "private_kernel_exposed": False,
    }


def _summary_markdown(inventory: dict[str, Any], gate: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {surface['product_name']} | {', '.join(surface['packages'])} | {surface['public_role']} |"
        for surface in inventory["surfaces"]
    )
    return f"""# ROE-1 Surface Alignment Summary

Decision: `{gate['decision']}`

ROE-1 aligns the current QIRA, AgentSec, and DataCapsule public surfaces under the same ResidualOps operating shape: packet or manifest intake, local check/probe/review, receipt/result artifact, ALLOW/HOLD/BLOCK decision, opt-in artifact bridge, and explicit claim boundary.

| Vertical | Packages | Public Role |
| --- | --- | --- |
{rows}

## Boundary

ROE-1 performs local repository checks only. It does not upload packages, submit MCP Registry metadata, enable GitHub workflows, call GitHub APIs, fetch URLs, execute external tools, request tokens, claim verification, certify security, guarantee quality, prove product readiness, or authorize actions. It does not enable workflows.
"""


def _next_steps_markdown(gate: dict[str, Any]) -> str:
    if gate["decision"] == "PASS_ROE1_SURFACE_ALIGNED":
        next_step = "ROE-2 shared artifact manifest and dashboard skeleton."
    else:
        next_step = "Remediate the listed HOLD/BLOCK findings before expanding the public surface."
    return f"""# ROE-1 Next Steps

Recommended next step: {next_step}

Keep using the same safe progression:

1. Preserve public/private split before adding discoverability.
2. Keep GitHub Actions as reusable actions and examples until a repository owner opts in.
3. Keep exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, and commercial routing policy non-public.
4. Treat ALLOW/HOLD/BLOCK as conservative routing labels, not certification or action authorization.
"""


def run_surface_alignment_gate(write_result: bool = True, root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    inventory = build_vertical_surface_inventory(root=base)
    alignment = run_public_private_alignment_audit(write_result=write_result, root=base)
    if inventory["decision"] == "BLOCK_ACTIVE_WORKFLOW_CREATED":
        decision = "BLOCK_ACTIVE_WORKFLOW_CREATED"
    elif alignment["decision"] == "BLOCK_PUBLIC_PRIVATE_LEAK":
        decision = "BLOCK_PUBLIC_PRIVATE_LEAK"
    elif alignment["decision"] == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
    elif inventory["decision"] == "HOLD_VERTICAL_SURFACE_MISSING":
        decision = "HOLD_VERTICAL_SURFACE_MISSING"
    else:
        decision = "PASS_ROE1_SURFACE_ALIGNED"
    gate = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "inventory_decision": inventory["decision"],
        "public_private_alignment_decision": alignment["decision"],
        "missing_paths": inventory["missing_paths"],
        "active_workflow_findings": inventory["active_workflow_findings"],
        "risky_phrase_count": alignment["risky_phrase_count"],
        "vertical_count": inventory["vertical_count"],
        "safe_to_continue_parallel_verticals": decision == "PASS_ROE1_SURFACE_ALIGNED",
        "recommended_next_package": "ROE-2 shared artifact manifest and dashboard skeleton"
        if decision == "PASS_ROE1_SURFACE_ALIGNED"
        else "ROE-1 remediation",
        "external_actions_performed": False,
        "workflow_enabled": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
        "private_kernel_exposed": False,
    }
    if write_result:
        _write_json(INVENTORY_PATH, inventory, root=base)
        _write_json(GATE_PATH, gate, root=base)
        _write_text(SUMMARY_PATH, _summary_markdown(inventory, gate), root=base)
        _write_text(NEXT_STEPS_PATH, _next_steps_markdown(gate), root=base)
    return gate


def main() -> None:
    result = run_surface_alignment_gate()
    print(f"residualops_surface_alignment: {result['decision']} verticals={result['vertical_count']}")


if __name__ == "__main__":
    main()
