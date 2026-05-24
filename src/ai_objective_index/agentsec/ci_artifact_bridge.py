from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .policy_gate import (
    SAMPLE_MANIFEST_SET,
    build_policy_gate_markdown,
    build_policy_gate_result,
    developer_default_profile,
    read_manifest_set,
    strict_enterprise_profile,
)


BridgeDecision = Literal[
    "PASS_AGENTSEC3_CI_ARTIFACT_BRIDGE",
    "HOLD_AGENTSEC3_MANIFEST_SET_REQUIRED",
    "HOLD_AGENTSEC3_POLICY_REVIEW",
    "BLOCK_AGENTSEC3_POLICY_RISK",
]

OUTPUT_DIR = Path("public_launch") / "agentsec3"
SAMPLE_MANIFEST_SET_PATH = OUTPUT_DIR / "AGENTSEC3_SAMPLE_MANIFEST_SET.json"
POLICY_GATE_RESULT_PATH = OUTPUT_DIR / "AGENTSEC3_POLICY_GATE_RESULT.json"
POLICY_GATE_REPORT_PATH = OUTPUT_DIR / "AGENTSEC3_POLICY_GATE_REPORT.md"
BRIDGE_RESULT_PATH = OUTPUT_DIR / "AGENTSEC3_BRIDGE_RESULT.json"
ACTION_MANIFEST_AUDIT_PATH = OUTPUT_DIR / "AGENTSEC3_ACTION_MANIFEST_AUDIT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "AGENTSEC3_NEXT_STEPS.md"


class AgentSecCiArtifactBridgeRequest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AgentSec_CiArtifactBridgeRequest/v0.1", alias="schema")
    manifest_set_path: str = ""
    output_dir: str = str(OUTPUT_DIR)
    profile: str = "developer_default"
    source: str = "github_actions"
    workflow_name: str = "AgentSec Policy Gate Artifact Bridge"
    job_name: str = "agentsec-policy-gate"
    commit_sha: str = ""
    branch: str = ""
    declared_claims: list[str] = Field(
        default_factory=lambda: ["Repository-supplied MCP/tool metadata for scoped AgentSec local review only."]
    )


class AgentSecCiArtifactBridgeResult(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="AgentSec_CiArtifactBridgeResult/v0.1", alias="schema")
    decision: BridgeDecision
    policy_gate_decision: str
    manifest_set_path: str
    policy_gate_result_path: str
    policy_gate_report_path: str
    output_dir: str
    profile: str = "developer_default"
    workflow_auto_enabled: bool = False
    active_workflow_created: bool = False
    external_actions_performed: bool = False
    live_mcp_called: bool = False
    external_tool_executed: bool = False
    url_fetch_performed: bool = False
    github_api_used_by_agentsec: bool = False
    token_printed: bool = False
    can_certify_security: bool = False
    can_certify_quality: bool = False
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
            raise ValueError("AgentSec-3 output directory must be inside the repository.") from exc
    return path


def _profile_from_name(name: str):
    if name == "strict_enterprise":
        return strict_enterprise_profile()
    return developer_default_profile()


def _bridge_decision(policy_decision: str) -> BridgeDecision:
    if policy_decision.startswith("BLOCK"):
        return "BLOCK_AGENTSEC3_POLICY_RISK"
    if policy_decision.startswith("HOLD"):
        return "HOLD_AGENTSEC3_POLICY_REVIEW"
    return "PASS_AGENTSEC3_CI_ARTIFACT_BRIDGE"


def write_next_steps(output_dir: Path = OUTPUT_DIR) -> Path:
    return _write_text(
        output_dir / "AGENTSEC3_NEXT_STEPS.md",
        """# AgentSec-3 Next Steps

1. Keep the workflow example in `examples/` until the repository owner opts in.
2. Feed repository-supplied MCP/tool manifests into the bridge from normal CI.
3. Publish AgentSec JSON/Markdown outputs as workflow artifacts only if the repository owner wants them.
4. Keep live proxy behavior, runtime sandboxing, external tool calls, and action authorization separately gated.

AgentSec-3 does not call live MCP servers, execute tools, fetch URLs, call GitHub APIs, post comments, handle tokens, certify security, guarantee quality, claim product readiness, or authorize external actions.
""",
    )


def run_ci_artifact_bridge(request: AgentSecCiArtifactBridgeRequest) -> AgentSecCiArtifactBridgeResult:
    output_dir = _resolve_output_dir(request.output_dir)
    if not request.manifest_set_path:
        result = AgentSecCiArtifactBridgeResult(
            decision="HOLD_AGENTSEC3_MANIFEST_SET_REQUIRED",
            policy_gate_decision="not_checked",
            manifest_set_path="",
            policy_gate_result_path=str(output_dir / "AGENTSEC3_POLICY_GATE_RESULT.json").replace("\\", "/"),
            policy_gate_report_path=str(output_dir / "AGENTSEC3_POLICY_GATE_REPORT.md").replace("\\", "/"),
            output_dir=str(output_dir).replace("\\", "/"),
            profile=request.profile,
            known_limits=["A local manifest set path is required."],
        )
        _write_json(output_dir / "AGENTSEC3_BRIDGE_RESULT.json", result.model_dump(mode="json", by_alias=True))
        write_next_steps(output_dir)
        return result

    payloads = read_manifest_set(Path(request.manifest_set_path))
    profile = _profile_from_name(request.profile)
    gate_result = build_policy_gate_result(payloads, profile=profile, manifest_set_path=request.manifest_set_path)
    _write_json(output_dir / "AGENTSEC3_POLICY_GATE_RESULT.json", gate_result.model_dump(mode="json", by_alias=True))
    _write_text(output_dir / "AGENTSEC3_POLICY_GATE_REPORT.md", build_policy_gate_markdown(gate_result))
    write_next_steps(output_dir)
    result = AgentSecCiArtifactBridgeResult(
        decision=_bridge_decision(gate_result.decision),
        policy_gate_decision=gate_result.decision,
        manifest_set_path=request.manifest_set_path,
        policy_gate_result_path=str(output_dir / "AGENTSEC3_POLICY_GATE_RESULT.json").replace("\\", "/"),
        policy_gate_report_path=str(output_dir / "AGENTSEC3_POLICY_GATE_REPORT.md").replace("\\", "/"),
        output_dir=str(output_dir).replace("\\", "/"),
        profile=request.profile,
        known_limits=[
            "AgentSec-3 converts opt-in workflow manifest metadata into local policy-gate artifacts.",
            "AgentSec-3 does not call live MCP servers, execute tools, fetch URLs, post comments, or call GitHub APIs.",
            "A bridge pass is not verification, security certification, quality guarantee, product readiness, or action authorization.",
        ],
    )
    _write_json(output_dir / "AGENTSEC3_BRIDGE_RESULT.json", result.model_dump(mode="json", by_alias=True))
    return result


def run_sample() -> AgentSecCiArtifactBridgeResult:
    _write_json(SAMPLE_MANIFEST_SET_PATH, SAMPLE_MANIFEST_SET)
    return run_ci_artifact_bridge(
        AgentSecCiArtifactBridgeRequest(
            manifest_set_path=str(SAMPLE_MANIFEST_SET_PATH).replace("\\", "/"),
            output_dir=str(OUTPUT_DIR),
            profile="developer_default",
            commit_sha="local-fixture",
            branch="sample",
        )
    )


def audit_agentsec3_action_manifest() -> dict[str, Any]:
    paths = [
        _repo_root() / ".github" / "actions" / "agentsec-policy-gate-artifact" / "action.yml",
        _repo_root() / "examples" / "agentsec_policy_gate_artifact_workflow.yml",
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
    ]
    findings: list[str] = []
    for path in paths:
        if not path.exists():
            findings.append(f"missing:{path.relative_to(_repo_root())}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        findings.extend(f"{path.relative_to(_repo_root())}:{item}" for item in forbidden if item in text)
    active_workflow = (_repo_root() / ".github" / "workflows" / "agentsec-policy-gate-artifact.yml").exists()
    result = {
        "decision": "PASS_AGENTSEC3_ACTION_MANIFEST_SAFE" if not findings and not active_workflow else "BLOCK_AGENTSEC3_ACTION_MANIFEST_UNSAFE",
        "manifest_exists": paths[0].exists(),
        "example_workflow_exists": paths[1].exists(),
        "active_workflow_created": active_workflow,
        "workflow_auto_enabled": False,
        "forbidden_command_findings": findings,
        "external_actions_performed": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "url_fetch_performed": False,
        "token_printed": False,
    }
    _write_json(ACTION_MANIFEST_AUDIT_PATH, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bridge opt-in CI manifest metadata into AgentSec policy-gate artifacts.")
    parser.add_argument("--run-sample", action="store_true", help="Write and review a safe AgentSec-3 sample.")
    parser.add_argument("--audit-manifest", action="store_true", help="Audit AgentSec-3 action and example workflow manifests.")
    parser.add_argument("--manifest-set", default="", help="Local JSON manifest, JSON list, or directory of JSON manifests.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Output directory for AgentSec-3 artifacts.")
    parser.add_argument("--profile", choices=["developer_default", "strict_enterprise"], default="developer_default")
    parser.add_argument("--workflow-name", default="AgentSec Policy Gate Artifact Bridge")
    parser.add_argument("--job-name", default="agentsec-policy-gate")
    parser.add_argument("--commit-sha", default="")
    parser.add_argument("--branch", default="")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_manifest:
        result = audit_agentsec3_action_manifest()
        print(f"agentsec3_action_manifest_audit: {result['decision']}")
        return
    if args.run_sample:
        result = run_sample()
    else:
        result = run_ci_artifact_bridge(
            AgentSecCiArtifactBridgeRequest(
                manifest_set_path=args.manifest_set,
                output_dir=args.output_dir,
                profile=args.profile,
                workflow_name=args.workflow_name,
                job_name=args.job_name,
                commit_sha=args.commit_sha,
                branch=args.branch,
            )
        )
    print(f"agentsec3_ci_artifact_bridge: {result.decision} policy={result.policy_gate_decision}")


if __name__ == "__main__":
    main()
