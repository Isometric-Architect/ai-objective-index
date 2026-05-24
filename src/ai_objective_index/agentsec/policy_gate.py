from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .manifest_scanner import SAMPLE_MANIFEST, build_action_boundary_receipt, scan_manifest_payload
from .models import AgentSecPolicyGateResult, AgentSecPolicyProfile, ToolRiskPacket


OUTPUT_DIR = Path("public_launch") / "agentsec2"
SAMPLE_MANIFEST_SET_PATH = OUTPUT_DIR / "AGENTSEC2_SAMPLE_MANIFEST_SET.json"
POLICY_PROFILE_PATH = OUTPUT_DIR / "AGENTSEC2_POLICY_PROFILE.json"
BATCH_SCAN_RESULT_PATH = OUTPUT_DIR / "AGENTSEC2_BATCH_SCAN_RESULT.json"
POLICY_GATE_REPORT_PATH = OUTPUT_DIR / "AGENTSEC2_POLICY_GATE_REPORT.md"
NEXT_STEPS_PATH = OUTPUT_DIR / "AGENTSEC2_NEXT_STEPS.md"


SAMPLE_MANIFEST_SET: list[dict[str, Any]] = [
    SAMPLE_MANIFEST,
    {
        "name": "repo-file-review-helper",
        "id": "fixture.local/repo-file-review-helper",
        "provider": "local-fixture",
        "integration_type": "mcp_server",
        "description": "Reads repository files supplied by the caller for local metadata review.",
        "permissions": {
            "network_access": False,
            "file_access": True,
            "write_access": False,
            "secret_access": False,
            "browser_access": False,
            "code_execution": False,
        },
    },
    {
        "name": "checkout-action-helper",
        "id": "fixture.local/checkout-action-helper",
        "provider": "local-fixture",
        "integration_type": "agent_tool",
        "description": "Fixture containing blocked language: complete payment and purchase flows.",
        "permissions": {
            "network_access": True,
            "file_access": False,
            "write_access": False,
            "secret_access": False,
            "browser_access": False,
            "code_execution": False,
        },
    },
]


def developer_default_profile() -> AgentSecPolicyProfile:
    return AgentSecPolicyProfile()


def strict_enterprise_profile() -> AgentSecPolicyProfile:
    return AgentSecPolicyProfile(
        profile_id="agentsec-strict-enterprise",
        name="AgentSec strict enterprise local metadata policy",
        mode="strict_enterprise",
        hold_on_network_access=True,
        hold_on_file_access=True,
        hold_on_write_access=True,
        hold_on_secret_access=True,
        hold_on_browser_access=True,
        hold_on_code_execution=True,
        hold_on_hidden_instruction=True,
    )


def _payloads_hash(payloads: list[dict[str, Any]], profile: AgentSecPolicyProfile) -> str:
    text = json.dumps(
        {"payloads": payloads, "profile": profile.model_dump(mode="json", by_alias=True)},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _permission_hold_reasons(packet: ToolRiskPacket, profile: AgentSecPolicyProfile) -> list[str]:
    checks = [
        ("network_access", profile.hold_on_network_access, packet.permission_scope.network_access),
        ("file_access", profile.hold_on_file_access, packet.permission_scope.file_access),
        ("write_access", profile.hold_on_write_access, packet.permission_scope.write_access),
        ("secret_access", profile.hold_on_secret_access, packet.permission_scope.secret_access),
        ("browser_access", profile.hold_on_browser_access, packet.permission_scope.browser_access),
        ("code_execution", profile.hold_on_code_execution, packet.permission_scope.code_execution),
    ]
    reasons = [f"{packet.tool_id}: policy holds {field}" for field, enabled, present in checks if enabled and present]
    if profile.require_namespace and packet.namespace_findings:
        reasons.append(f"{packet.tool_id}: policy requires namespace/ownership review")
    if profile.hold_on_hidden_instruction and packet.hidden_instruction_findings:
        reasons.append(f"{packet.tool_id}: policy holds hidden-instruction indicators")
    return reasons


def _block_reasons(packet: ToolRiskPacket, profile: AgentSecPolicyProfile) -> list[str]:
    reasons: list[str] = []
    if profile.block_on_forbidden_action and packet.forbidden_action_findings:
        reasons.append(f"{packet.tool_id}: forbidden action language")
    if profile.block_on_unsupported_claim and packet.unsupported_claim_findings:
        reasons.append(f"{packet.tool_id}: unsupported claim language")
    return reasons


def apply_policy_profile(packet: ToolRiskPacket, profile: AgentSecPolicyProfile) -> tuple[ToolRiskPacket, list[str], list[str]]:
    updated = packet.model_copy(deep=True)
    hold_reasons = _permission_hold_reasons(updated, profile)
    block_reasons = _block_reasons(updated, profile)
    if block_reasons:
        if updated.forbidden_action_findings:
            updated.risk_decision = "BLOCK_FORBIDDEN_ACTION"
        else:
            updated.risk_decision = "BLOCK_UNSUPPORTED_CLAIM"
        updated.blocked_use = sorted(
            set(updated.blocked_use + ["agent routing under this policy until blocked language is removed or separately justified"])
        )
    elif hold_reasons and updated.risk_decision == "ALLOW_METADATA_ONLY":
        updated.risk_decision = "HOLD_REVIEW_REQUIRED"
        updated.hold_use = sorted(set(updated.hold_use + ["agent routing under this policy until permission review is complete"]))
    if hold_reasons or block_reasons:
        updated.residual_notes = sorted(set(updated.residual_notes + hold_reasons + block_reasons))
    return updated, hold_reasons, block_reasons


def build_policy_gate_result(
    payloads: list[dict[str, Any]],
    profile: AgentSecPolicyProfile | None = None,
    manifest_set_path: str = "<memory>",
) -> AgentSecPolicyGateResult:
    active_profile = profile or developer_default_profile()
    packets: list[ToolRiskPacket] = []
    hold_reasons: list[str] = []
    block_reasons: list[str] = []
    for index, payload in enumerate(payloads):
        base_packet = scan_manifest_payload(payload, f"{manifest_set_path}#{index}")
        packet, packet_holds, packet_blocks = apply_policy_profile(base_packet, active_profile)
        packets.append(packet)
        hold_reasons.extend(packet_holds)
        block_reasons.extend(packet_blocks)
    allow_count = sum(1 for packet in packets if packet.risk_decision == "ALLOW_METADATA_ONLY")
    hold_count = sum(1 for packet in packets if packet.risk_decision == "HOLD_REVIEW_REQUIRED")
    block_count = sum(1 for packet in packets if packet.risk_decision.startswith("BLOCK"))
    if block_count:
        decision = "BLOCK_AGENTSEC2_POLICY_RISK"
    elif hold_count:
        decision = "HOLD_AGENTSEC2_REVIEW_REQUIRED"
    else:
        decision = "PASS_AGENTSEC2_POLICY_GATE"
    return AgentSecPolicyGateResult(
        gate_id=f"agentsec2-gate-{_payloads_hash(payloads, active_profile)}",
        decision=decision,
        profile=active_profile,
        manifest_set_path=manifest_set_path,
        packet_count=len(packets),
        allow_count=allow_count,
        hold_count=hold_count,
        block_count=block_count,
        policy_hold_reasons=sorted(set(hold_reasons)),
        policy_block_reasons=sorted(set(block_reasons)),
        packets=packets,
        receipts=[build_action_boundary_receipt(packet) for packet in packets],
        known_limits=[
            "local metadata policy gate only",
            "no live MCP call",
            "no external tool execution",
            "no URL fetch",
            "not verification",
            "not security certification",
            "not action authorization",
        ],
    )


def build_policy_gate_markdown(result: AgentSecPolicyGateResult) -> str:
    rows = "\n".join(
        f"| `{packet.tool_id}` | `{packet.risk_decision}` | `{packet.integration_type}` | `{packet.provider}` |"
        for packet in result.packets
    )
    holds = "\n".join(f"- {item}" for item in result.policy_hold_reasons) or "- No policy hold reasons recorded."
    blocks = "\n".join(f"- {item}" for item in result.policy_block_reasons) or "- No policy block reasons recorded."
    return f"""# AgentSec-2 Policy Gate Report

Decision: `{result.decision}`

| Field | Value |
| --- | --- |
| Profile | `{result.profile.profile_id}` |
| Packets | `{result.packet_count}` |
| ALLOW metadata-only | `{result.allow_count}` |
| HOLD review | `{result.hold_count}` |
| BLOCK policy risk | `{result.block_count}` |
| Live MCP calls | `False` |
| External tool execution | `False` |
| URL fetch | `False` |

## Packet Decisions

| Tool | Decision | Integration | Provider |
| --- | --- | --- | --- |
{rows}

## Hold Reasons

{holds}

## Block Reasons

{blocks}

## Boundaries

AgentSec-2 is a local metadata policy gate. It does not certify security, guarantee quality, claim product readiness, execute tools, call live MCP servers, fetch URLs, handle tokens, or authorize external actions.
"""


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def read_manifest_set(path: Path) -> list[dict[str, Any]]:
    resolved = path if path.is_absolute() else _repo_root() / path
    if resolved.is_dir():
        payloads = []
        for child in sorted(resolved.glob("*.json")):
            payload = json.loads(child.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                payloads.append(payload)
        return payloads
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        return [payload]
    return []


def build_agentsec2_sample_outputs() -> AgentSecPolicyGateResult:
    profile = developer_default_profile()
    result = build_policy_gate_result(
        SAMPLE_MANIFEST_SET,
        profile=profile,
        manifest_set_path=str(SAMPLE_MANIFEST_SET_PATH).replace("\\", "/"),
    )
    _write_json(SAMPLE_MANIFEST_SET_PATH, SAMPLE_MANIFEST_SET)
    _write_json(POLICY_PROFILE_PATH, profile.model_dump(mode="json", by_alias=True))
    _write_json(BATCH_SCAN_RESULT_PATH, result.model_dump(mode="json", by_alias=True))
    _write_text(POLICY_GATE_REPORT_PATH, build_policy_gate_markdown(result))
    _write_text(
        NEXT_STEPS_PATH,
        """# AgentSec-2 Next Steps

1. Add repository-supplied manifest directory intake to the optional CI bridge.
2. Add private enterprise policy profiles outside the public repo when exact thresholds or provider priors are needed.
3. Keep live proxy behavior, runtime sandboxing, and action authorization out of scope until separately gated.
""",
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AgentSec-2 local multi-manifest policy gate.")
    parser.add_argument("--manifest-set", type=Path, help="Local JSON manifest file, JSON list, or directory of JSON manifests.")
    parser.add_argument("--profile", choices=["developer_default", "strict_enterprise"], default="developer_default")
    parser.add_argument("--run-sample", action="store_true", help="Write sample AgentSec-2 public outputs.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.profile == "strict_enterprise":
        profile = strict_enterprise_profile()
    else:
        profile = developer_default_profile()
    if args.manifest_set:
        payloads = read_manifest_set(args.manifest_set)
        result = build_policy_gate_result(payloads, profile=profile, manifest_set_path=str(args.manifest_set).replace("\\", "/"))
        print(f"agentsec2_gate: {result.decision} packets={result.packet_count}")
        return
    result = build_agentsec2_sample_outputs()
    print(f"agentsec2_sample: {result.decision} packets={result.packet_count}")


if __name__ == "__main__":
    main()
