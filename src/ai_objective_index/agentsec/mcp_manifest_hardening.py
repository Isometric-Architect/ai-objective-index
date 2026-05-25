from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json


OUTPUT_DIR = Path("public_launch") / "agentsec4"
HARDENING_RESULT_PATH = OUTPUT_DIR / "AGENTSEC4_MCP_MANIFEST_HARDENING_RESULT.json"
HARDENING_REPORT_PATH = OUTPUT_DIR / "AGENTSEC4_MCP_MANIFEST_HARDENING_REPORT.md"

DEFAULT_TOOL_MANIFEST = Path("data") / "generated_mcp_tools_manifest.json"
DEFAULT_SERVER_JSON = Path(".mcp") / "server.json"

FORBIDDEN_ACTION_TERMS = [
    "payment",
    "booking",
    "login",
    "email",
    "form submission",
    "purchase",
    "contract",
    "account connection",
    "supplier claim",
    "supplier verification",
]
UNSUPPORTED_CLAIM_TERMS = [
    "verified tool",
    "safe tool",
    "security certified",
    "quality guaranteed",
    "production ready",
    "action authorized",
    "automatic security gateway",
]
SAFE_CONTEXT = ["not ", "no ", "never ", "must not", "do not", "does not", "without ", "cannot "]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _safe_text(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in SAFE_CONTEXT)


def _risky_terms(text: str, terms: list[str]) -> list[str]:
    findings = []
    lowered = text.lower()
    for term in terms:
        if re.search(rf"\b{re.escape(term)}\b", lowered) and not _safe_text(lowered):
            findings.append(term)
    return findings


def _tool_findings(tool: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    name = str(tool.get("name") or "<unnamed>")
    if tool.get("read_only") is not True:
        findings.append(f"{name}: read_only is not true")
    text = json.dumps(tool, ensure_ascii=False)
    for term in _risky_terms(text, FORBIDDEN_ACTION_TERMS):
        findings.append(f"{name}: forbidden action term without safe context: {term}")
    for term in _risky_terms(text, UNSUPPORTED_CLAIM_TERMS):
        findings.append(f"{name}: unsupported claim term without safe context: {term}")
    if "input_schema" not in tool:
        findings.append(f"{name}: input_schema missing")
    if "output_schema" not in tool:
        findings.append(f"{name}: output_schema missing")
    return findings


def build_mcp_manifest_hardening_result(
    tool_manifest_path: Path | None = None,
    server_json_path: Path | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    tool_path = base / (tool_manifest_path or DEFAULT_TOOL_MANIFEST)
    server_path = base / (server_json_path or DEFAULT_SERVER_JSON)
    tool_manifest = _read_json(tool_path)
    server_json = _read_json(server_path)
    findings: list[str] = []
    warnings: list[str] = []

    if not tool_manifest:
        findings.append("MCP tools manifest missing or invalid JSON")
    if not server_json:
        findings.append(".mcp/server.json missing or invalid JSON")

    if tool_manifest and tool_manifest.get("read_only") is not True:
        findings.append("tools manifest read_only is not true")
    tools = tool_manifest.get("tools", []) if isinstance(tool_manifest.get("tools"), list) else []
    if not tools:
        findings.append("tools manifest has no tools")
    for tool in tools:
        if isinstance(tool, dict):
            findings.extend(_tool_findings(tool))

    forbidden_actions = tool_manifest.get("forbidden_actions", [])
    for expected in ["payment", "booking", "login", "purchase", "contract_signing", "account_connection"]:
        if expected not in forbidden_actions:
            warnings.append(f"forbidden_actions missing expected term: {expected}")

    if server_json and server_json.get("read_only") is not True:
        findings.append("server.json read_only is not true")
    limitations = " ".join(str(item) for item in server_json.get("limitations", []))
    for phrase in ["not verified", "not security certified", "not a quality guarantee"]:
        if phrase not in limitations.lower():
            warnings.append(f"server.json limitations should include: {phrase}")
    if server_json and server_json.get("vnext_surfaces", {}).get("external_action_authorization") is not False:
        findings.append("server.json external_action_authorization is not false")
    if server_json and server_json.get("vnext_surfaces", {}).get("external_tool_execution") is not False:
        findings.append("server.json external_tool_execution is not false")
    if server_json and server_json.get("vnext_surfaces", {}).get("live_mcp_calls") is not False:
        findings.append("server.json live_mcp_calls is not false")

    text_blob = json.dumps({"tool_manifest": tool_manifest, "server_json": server_json}, ensure_ascii=False)
    if _risky_terms(text_blob, UNSUPPORTED_CLAIM_TERMS):
        findings.append("unsupported positive claim appears without safe context")

    if findings:
        decision = "BLOCK_AGENTSEC4_MCP_MANIFEST_RISK"
    elif warnings:
        decision = "HOLD_AGENTSEC4_MCP_MANIFEST_REVIEW"
    else:
        decision = "PASS_AGENTSEC4_MCP_MANIFEST_HARDENED"
    return {
        "schema": "AgentSec_McpManifestHardeningResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "tool_manifest_path": str(tool_manifest_path or DEFAULT_TOOL_MANIFEST).replace("\\", "/"),
        "server_json_path": str(server_json_path or DEFAULT_SERVER_JSON).replace("\\", "/"),
        "tool_count": len(tools),
        "findings": findings,
        "warnings": warnings,
        "read_only": tool_manifest.get("read_only") is True and server_json.get("read_only") is True,
        "local_only": True,
        "network_used": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "token_printed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
        "known_limits": [
            "static MCP manifest hardening only",
            "no live MCP call",
            "no external tool execution",
            "no URL fetch",
            "not security certification",
            "not quality guarantee",
            "not action authorization",
        ],
    }


def build_hardening_report(result: dict[str, Any]) -> str:
    findings = "\n".join(f"- {item}" for item in result["findings"]) or "- No blocking findings."
    warnings = "\n".join(f"- {item}" for item in result["warnings"]) or "- No warnings."
    return f"""# AgentSec-4 MCP Manifest Hardening Report

Decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Tool manifest | `{result['tool_manifest_path']}` |
| Server JSON | `{result['server_json_path']}` |
| Tool count | `{result['tool_count']}` |
| Read only | `{result['read_only']}` |
| Live MCP called | `False` |
| External tool executed | `False` |
| Network used | `False` |

## Findings

{findings}

## Warnings

{warnings}

## Boundary

This report is a static manifest hardening check. It is not security certification, a quality guarantee, product-readiness evidence, live gateway protection, or action authorization.
"""


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def write_mcp_manifest_hardening_result() -> dict[str, Any]:
    result = build_mcp_manifest_hardening_result()
    _write_json(HARDENING_RESULT_PATH, result)
    _write_text(HARDENING_REPORT_PATH, build_hardening_report(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AgentSec-4 static MCP manifest hardening checks.")
    parser.add_argument("--write-sample", action="store_true", help="Write AgentSec-4 MCP manifest hardening outputs.")
    return parser


def main() -> None:
    build_parser().parse_args()
    result = write_mcp_manifest_hardening_result()
    print(f"agentsec4_mcp_manifest_hardening: {result['decision']} tools={result['tool_count']}")


if __name__ == "__main__":
    main()
