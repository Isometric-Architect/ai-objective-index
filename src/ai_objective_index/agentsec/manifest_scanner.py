from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .models import (
    AgentSecActionBoundaryReceipt,
    AgentSecScanResult,
    PermissionScope,
    RiskDecision,
    ToolRiskPacket,
)


OUTPUT_DIR = Path("public_launch") / "agentsec1"
SAMPLE_MANIFEST_PATH = OUTPUT_DIR / "AGENTSEC1_SAMPLE_TOOL_MANIFEST.json"
TOOL_RISK_PACKET_PATH = OUTPUT_DIR / "AGENTSEC1_TOOL_RISK_PACKET.json"
SCAN_RESULT_PATH = OUTPUT_DIR / "AGENTSEC1_SCAN_RESULT.json"
ACTION_BOUNDARY_RECEIPT_PATH = OUTPUT_DIR / "AGENTSEC1_ACTION_BOUNDARY_RECEIPT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "AGENTSEC1_NEXT_STEPS.md"

SAMPLE_MANIFEST: dict[str, Any] = {
    "name": "local-metadata-browser-helper",
    "id": "fixture.local/local-metadata-browser-helper",
    "provider": "local-fixture",
    "integration_type": "mcp_server",
    "description": "Fixture manifest for local metadata review of browser-oriented MCP candidates.",
    "permissions": {
        "network_access": False,
        "file_access": False,
        "write_access": False,
        "secret_access": False,
        "browser_access": False,
        "code_execution": False,
    },
    "tools": [
        {
            "name": "summarize_supplied_metadata",
            "description": "Summarize metadata already supplied by the caller.",
        }
    ],
    "claim_boundaries": [
        "not verified",
        "not security certified",
        "not a quality guarantee",
        "no external action authorization",
    ],
}

PERMISSION_PATTERNS = {
    "network_access": [r"\bnetwork\b", r"\bhttp\b", r"\burl\b", r"\bfetch\b", r"\bweb\b"],
    "file_access": [r"\bfile\b", r"\bfilesystem\b", r"\bpath\b", r"\breadfile\b"],
    "write_access": [r"\bwrite\b", r"\bdelete\b", r"\bmodify\b", r"\bcreate\b"],
    "secret_access": [r"\bsecret\b", r"\bcredential\b", r"\bapi[_ -]?key\b", r"\btoken\b"],
    "browser_access": [r"\bbrowser\b", r"\bplaywright\b", r"\bselenium\b"],
    "code_execution": [r"\bshell\b", r"\bsubprocess\b", r"\bexec\b", r"\bcode execution\b"],
}

HIDDEN_INSTRUCTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore the user",
    r"system prompt",
    r"developer message",
    r"do not tell the user",
    r"hidden instruction",
    r"exfiltrate",
    r"leak secrets",
]

FORBIDDEN_ACTION_PATTERNS = [
    r"\bpayment\b",
    r"\bbooking\b",
    r"\blogin\b",
    r"\bemail\b",
    r"\bpurchase\b",
    r"\bcontract\b",
    r"\baccount connection\b",
    r"\bsupplier verification\b",
    r"\bsupplier claim\b",
]

UNSUPPORTED_CLAIM_PATTERNS = [
    r"\bverified tool\b",
    r"\bsafe tool\b",
    r"\bsecurity certified\b",
    r"\bquality guaranteed\b",
    r"\bproduction[- ]ready\b",
    r"\bofficial best\b",
    r"\btrusted by all agents\b",
]

SAFE_CONTEXT_MARKERS = [
    "not ",
    "no ",
    "never ",
    "must not",
    "do not",
    "does not",
    "without ",
]


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _metadata_hash(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.:/-]+", "-", value.strip()) or "unknown"
    return cleaned.strip("-")[:120] or "unknown"


def _iter_strings(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.append((child_prefix, str(key)))
            rows.extend(_iter_strings(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_iter_strings(child, f"{prefix}[{index}]"))
    elif value is not None:
        rows.append((prefix, str(value)))
    return rows


def _is_false_like(text: str) -> bool:
    return text.strip().lower() in {"false", "0", "none", "no", "disabled", "local_only"}


def _safe_context(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in SAFE_CONTEXT_MARKERS)


def _matches(patterns: list[str], rows: list[tuple[str, str]], skip_safe_context: bool = True) -> list[str]:
    findings: list[str] = []
    compiled = [re.compile(pattern, re.I) for pattern in patterns]
    for path, text in rows:
        if _is_false_like(text):
            continue
        haystack = f"{path}: {text}"
        if skip_safe_context and _safe_context(haystack):
            continue
        for pattern in compiled:
            if pattern.search(haystack):
                findings.append(haystack[:240])
                break
    return sorted(set(findings))


def _extract_permission_scope(payload: dict[str, Any]) -> PermissionScope:
    rows = _iter_strings(payload)
    indicators_by_field: dict[str, list[str]] = {}
    values: dict[str, bool] = {}
    for field, patterns in PERMISSION_PATTERNS.items():
        findings = _matches(patterns, rows, skip_safe_context=True)
        values[field] = bool(findings)
        indicators_by_field[field] = [f"{field}: {finding}" for finding in findings[:5]]
    permissions = payload.get("permissions")
    if isinstance(permissions, dict):
        for field in PERMISSION_PATTERNS:
            if isinstance(permissions.get(field), bool):
                values[field] = bool(permissions[field])
                if permissions[field] is False:
                    indicators_by_field[field] = []
    indicators = [indicator for field_indicators in indicators_by_field.values() for indicator in field_indicators]
    return PermissionScope(raw_indicators=sorted(set(indicators))[:30], **values)


def _extract_identity(payload: dict[str, Any]) -> tuple[str, str, str, str]:
    name = str(payload.get("name") or payload.get("title") or payload.get("server_name") or "unknown-tool")
    tool_id = str(payload.get("id") or payload.get("tool_id") or payload.get("name") or name)
    provider = str(payload.get("provider") or payload.get("author") or payload.get("repository") or "unknown")
    integration_type = str(payload.get("integration_type") or payload.get("type") or "unknown")
    if "mcp" in _stable_json(payload).lower() or "server" in payload:
        integration_type = "mcp_server"
    if integration_type not in {"mcp_server", "tool_manifest", "api", "agent_tool", "unknown"}:
        integration_type = "unknown"
    return _slug(tool_id), name[:160], provider[:160], integration_type


def _namespace_findings(tool_id: str, name: str) -> list[str]:
    findings: list[str] = []
    if tool_id in {"unknown", "unknown-tool"}:
        findings.append("missing stable tool id or namespace")
    if "/" not in tool_id and "." not in tool_id:
        findings.append("tool id lacks namespace separator")
    lowered = f"{tool_id} {name}".lower()
    if "official" in lowered:
        findings.append("uses official-like naming; ownership evidence needed")
    if "0penai" in lowered or "micros0ft" in lowered or "g00gle" in lowered:
        findings.append("lookalike provider spelling detected")
    return findings


def _decision(
    permission_scope: PermissionScope,
    hidden: list[str],
    injection: list[str],
    namespace: list[str],
    forbidden: list[str],
    unsupported: list[str],
) -> RiskDecision:
    if forbidden:
        return "BLOCK_FORBIDDEN_ACTION"
    if unsupported:
        return "BLOCK_UNSUPPORTED_CLAIM"
    if hidden or injection or namespace:
        return "HOLD_REVIEW_REQUIRED"
    if any(
        [
            permission_scope.network_access,
            permission_scope.file_access,
            permission_scope.write_access,
            permission_scope.secret_access,
            permission_scope.browser_access,
            permission_scope.code_execution,
        ]
    ):
        return "HOLD_REVIEW_REQUIRED"
    return "ALLOW_METADATA_ONLY"


def scan_manifest_payload(payload: dict[str, Any], manifest_path: str = "<memory>") -> ToolRiskPacket:
    rows = _iter_strings(payload)
    tool_id, name, provider, integration_type = _extract_identity(payload)
    permission_scope = _extract_permission_scope(payload)
    hidden = _matches(HIDDEN_INSTRUCTION_PATTERNS, rows, skip_safe_context=False)
    injection = [finding for finding in hidden if "ignore" in finding.lower() or "prompt" in finding.lower()]
    namespace = _namespace_findings(tool_id, name)
    forbidden = _matches(FORBIDDEN_ACTION_PATTERNS, rows, skip_safe_context=True)
    unsupported = _matches(UNSUPPORTED_CLAIM_PATTERNS, rows, skip_safe_context=True)
    risk_decision = _decision(permission_scope, hidden, injection, namespace, forbidden, unsupported)
    hold_use: list[str] = []
    blocked_use: list[str] = []
    if risk_decision == "HOLD_REVIEW_REQUIRED":
        hold_use.append("agent tool routing until permissions, ownership, and instruction boundaries are reviewed")
    if risk_decision == "BLOCK_FORBIDDEN_ACTION":
        blocked_use.append("tool use under requested scope because forbidden real-world action language was detected")
    if risk_decision == "BLOCK_UNSUPPORTED_CLAIM":
        blocked_use.append("tool use under requested scope because unsupported verification/safety/readiness claim was detected")
    residuals = []
    if permission_scope.raw_indicators:
        residuals.append("permission indicators require human review before any live execution path")
    if namespace:
        residuals.append("namespace or ownership evidence is incomplete")
    if not residuals:
        residuals.append("metadata-only scan found no blocking indicators; this is still not verification")
    return ToolRiskPacket(
        packet_id=f"agentsec-risk-{hashlib.sha1(tool_id.encode('utf-8')).hexdigest()[:12]}",
        tool_id=tool_id,
        name=name,
        provider=provider,
        manifest_path=manifest_path,
        metadata_hash=_metadata_hash(payload),
        integration_type=integration_type,  # type: ignore[arg-type]
        permission_scope=permission_scope,
        hidden_instruction_findings=hidden,
        prompt_injection_findings=injection,
        namespace_findings=namespace,
        forbidden_action_findings=forbidden,
        unsupported_claim_findings=unsupported,
        risk_decision=risk_decision,
        hold_use=hold_use,
        blocked_use=blocked_use,
        residual_notes=residuals,
    )


def build_action_boundary_receipt(packet: ToolRiskPacket) -> AgentSecActionBoundaryReceipt:
    hold_actions = []
    blocked_actions = []
    if packet.risk_decision == "HOLD_REVIEW_REQUIRED":
        hold_actions.append("live tool execution")
    if packet.risk_decision.startswith("BLOCK"):
        blocked_actions.extend(["live tool execution", "agent delegation", "external action"])
    blocked_actions.extend(
        [
            "payment",
            "booking",
            "login",
            "email sending",
            "purchase",
            "contract signing",
            "account connection",
        ]
    )
    return AgentSecActionBoundaryReceipt(
        receipt_id=f"agentsec-receipt-{packet.packet_id.removeprefix('agentsec-risk-')}",
        packet_id=packet.packet_id,
        decision=packet.risk_decision,
        hold_actions=sorted(set(hold_actions)),
        blocked_actions=sorted(set(blocked_actions)),
    )


def build_scan_result(packet: ToolRiskPacket, manifest_path: str) -> AgentSecScanResult:
    receipt = build_action_boundary_receipt(packet)
    allow_count = 1 if packet.risk_decision == "ALLOW_METADATA_ONLY" else 0
    hold_count = 1 if packet.risk_decision == "HOLD_REVIEW_REQUIRED" else 0
    block_count = 1 if packet.risk_decision.startswith("BLOCK") else 0
    if block_count:
        decision = "BLOCK_AGENTSEC1_MANIFEST_RISK"
    elif hold_count:
        decision = "HOLD_AGENTSEC1_REVIEW_REQUIRED"
    else:
        decision = "PASS_AGENTSEC1_LOCAL_SCAN"
    return AgentSecScanResult(
        scan_id=f"agentsec-scan-{packet.packet_id.removeprefix('agentsec-risk-')}",
        decision=decision,
        manifest_path=manifest_path,
        packet_count=1,
        allow_count=allow_count,
        hold_count=hold_count,
        block_count=block_count,
        packets=[packet],
        receipts=[receipt],
        known_limits=[
            "local metadata scan only",
            "no live MCP call",
            "no external tool execution",
            "not verification",
            "not security certification",
            "not action authorization",
        ],
    )


def scan_manifest_path(path: Path) -> AgentSecScanResult:
    resolved = path if path.is_absolute() else _repo_root() / path
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    packet = scan_manifest_payload(payload, str(path).replace("\\", "/"))
    return build_scan_result(packet, str(path).replace("\\", "/"))


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def build_agentsec1_sample_outputs() -> AgentSecScanResult:
    _write_json(SAMPLE_MANIFEST_PATH, SAMPLE_MANIFEST)
    packet = scan_manifest_payload(SAMPLE_MANIFEST, str(SAMPLE_MANIFEST_PATH).replace("\\", "/"))
    receipt = build_action_boundary_receipt(packet)
    result = build_scan_result(packet, str(SAMPLE_MANIFEST_PATH).replace("\\", "/"))
    _write_json(TOOL_RISK_PACKET_PATH, packet.model_dump(mode="json", by_alias=True))
    _write_json(ACTION_BOUNDARY_RECEIPT_PATH, receipt.model_dump(mode="json", by_alias=True))
    _write_json(SCAN_RESULT_PATH, result.model_dump(mode="json", by_alias=True))
    _write_text(
        NEXT_STEPS_PATH,
        """# AgentSec-1 Next Steps

1. Add local manifest intake for repository-supplied MCP server metadata.
2. Add optional policy profiles for enterprise review while keeping exact private thresholds non-public.
3. Keep live proxy behavior, external tool calls, and action authorization out of scope until separately gated.
""",
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AgentSec-1 local MCP/tool manifest metadata scan.")
    parser.add_argument("--manifest", type=Path, help="Path to a local JSON MCP/tool manifest.")
    parser.add_argument("--run-sample", action="store_true", help="Write sample AgentSec-1 public outputs.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.manifest:
        result = scan_manifest_path(args.manifest)
        print(f"agentsec_scan: {result.decision} packets={result.packet_count}")
        return
    result = build_agentsec1_sample_outputs()
    print(f"agentsec_sample: {result.decision} packets={result.packet_count}")


if __name__ == "__main__":
    main()
