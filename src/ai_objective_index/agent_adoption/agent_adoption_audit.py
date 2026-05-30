from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from . import read_json, repo_root, timestamp, write_json
from .agent_claim_boundary import scan_paths
from .capability_card import CAPABILITY_CARD_PATH, build_capability_card, validate_capability_card


OUTPUT_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_ADOPTION_AUDIT_RESULT.json"

REQUIRED_ARTIFACTS = [
    Path("agent_discovery") / "CAPABILITY_CARD.json",
    Path("agent_discovery") / "CAPABILITY_CARD.md",
    Path("agent_discovery") / "WHEN_TO_USE_AOI.md",
    Path("agent_discovery") / "WHEN_NOT_TO_USE_AOI.md",
    Path("agent_discovery") / "AGENT_DISCOVER_MODE.md",
    Path("agent_discovery") / "AGENT_PREFLIGHT_MODE.md",
    Path("agent_discovery") / "MCP_AGENT_PROMPTS.md",
    Path("agent_discovery") / "OPENAPI_AGENT_EXAMPLES.md",
    Path("agent_discovery") / "AGENT_OUTPUT_SCHEMA_EXAMPLES.json",
    Path("agent_discovery") / "AGENT_CLAIM_BOUNDARY.md",
    Path("agent_discovery") / "FRESHNESS_AND_STALENESS_POLICY.md",
    Path("agent_discovery") / "RESIDUALOPS_EXTENSION_MAP.md",
    Path("agent_discovery") / "ORDINARY_AGENT_FAILURE_MODES.md",
    Path("agent_discovery") / "PRIVATE_KERNEL_NONDISCLOSURE.md",
    Path("examples") / "agent_prompts" / "discover_mcp_candidates.md",
    Path("examples") / "agent_prompts" / "preflight_mcp_candidate.md",
    Path("api") / "vnext" / "examples" / "agent" / "discover_request.json",
    Path("api") / "vnext" / "examples" / "agent" / "discover_response.json",
    Path("api") / "vnext" / "examples" / "agent" / "preflight_request.json",
    Path("api") / "vnext" / "examples" / "agent" / "preflight_response.json",
]

TOKEN_PATTERN = re.compile(r"\b(sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9_]{12,}|hf_[A-Za-z0-9]{12,}|PRIVATE KEY|api_key\s*=)", re.I)
ACTION_AUTH_PATTERN = re.compile(r"\b(action authorized|authorized to execute|authorized to deploy|authorized to merge)\b", re.I)


def _artifact_paths() -> list[Path]:
    root = repo_root()
    paths: list[Path] = []
    for directory in ["agent_discovery", "examples/agent_prompts", "api/vnext/examples/agent", "docs"]:
        full = root / directory
        if not full.exists():
            continue
        for child in full.rglob("*"):
            if child.is_file() and child.suffix.lower() in {".md", ".json", ".txt"}:
                if directory == "docs" and not child.name.startswith("aoi_"):
                    continue
                paths.append(child)
    return paths


def run_agent_adoption_audit(write_result: bool = True) -> dict[str, Any]:
    root = repo_root()
    missing_artifacts = [str(path).replace("\\", "/") for path in REQUIRED_ARTIFACTS if not (root / path).exists()]
    card = read_json(CAPABILITY_CARD_PATH) or build_capability_card()
    card_missing = validate_capability_card(card)
    paths = _artifact_paths()
    overclaim_findings = scan_paths(paths)
    secret_findings: list[dict[str, Any]] = []
    action_auth_findings: list[dict[str, Any]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if TOKEN_PATTERN.search(line):
                secret_findings.append({"path": str(path), "line": line_number, "text": line.strip()[:180]})
            if ACTION_AUTH_PATTERN.search(line) and "not " not in line.lower() and "no " not in line.lower() and "must not" not in line.lower():
                action_auth_findings.append({"path": str(path), "line": line_number, "text": line.strip()[:180]})

    private_findings = [finding for finding in overclaim_findings if finding["kind"] == "private_kernel_value"]
    risky_findings = [finding for finding in overclaim_findings if finding["kind"] == "overclaim"]

    if private_findings:
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
    elif risky_findings:
        decision = "BLOCK_OVERCLAIM"
    elif secret_findings:
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
    elif action_auth_findings:
        decision = "BLOCK_ACTION_AUTHORIZATION"
    elif missing_artifacts or card_missing:
        decision = "HOLD_MISSING_AGENT_ARTIFACT"
    else:
        decision = "PASS_AGENT_NATIVE_DISCOVERY_READY"

    result = {
        "schema": "AOI_AgentAdoptionAudit/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "capability_card_valid": not card_missing,
        "capability_card_missing": card_missing,
        "required_artifact_count": len(REQUIRED_ARTIFACTS),
        "missing_artifacts": missing_artifacts,
        "scanned_artifacts": [str(path.relative_to(root)).replace("\\", "/") for path in paths if root in path.parents],
        "overclaim_findings": risky_findings,
        "private_kernel_findings": private_findings,
        "secret_findings": secret_findings,
        "action_authorization_findings": action_auth_findings,
        "private_kernel_not_disclosed": not private_findings,
        "product_or_security_certification_claim": False,
        "external_action_authorization_claim": bool(action_auth_findings),
        "external_api_used": False,
        "live_mcp_call_used": False,
        "pypi_upload_performed": False,
        "mcp_registry_publish_performed": False,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
        write_json(Path("agent_discovery") / "AGENT_ADOPTION_AUDIT_RESULT.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_agent_adoption_audit()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"agent_adoption_audit: {result['decision']} missing={len(result['missing_artifacts'])}")


if __name__ == "__main__":
    main()

