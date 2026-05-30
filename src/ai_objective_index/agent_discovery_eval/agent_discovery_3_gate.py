from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import (
    AOI_GUIDED_RESULTS_PATH,
    EVAL_CASES_PATH,
    EVAL_REPORT_PATH,
    GATE_PATH,
    MANUAL_EVAL_SHEET_PATH,
    MCP_REGISTRY_PUBLIC_SMOKE_PATH,
    NAIVE_BASELINE_PATH,
    PUBLIC_DISCOVERY_SMOKE_PATH,
    PYPI_PUBLIC_INSTALL_SMOKE_PATH,
    read_json,
    read_list,
    read_text,
    timestamp,
    write_json,
)


REQUIRED_GUIDED_KEYS = [
    "top_candidates",
    "source_traces",
    "missing_fields",
    "route_decision",
    "next_action",
    "must_not_claim",
    "residualops_escalation",
    "freshness",
]

ARTIFACT_PATHS = [
    PUBLIC_DISCOVERY_SMOKE_PATH,
    PYPI_PUBLIC_INSTALL_SMOKE_PATH,
    MCP_REGISTRY_PUBLIC_SMOKE_PATH,
    EVAL_CASES_PATH,
    NAIVE_BASELINE_PATH,
    AOI_GUIDED_RESULTS_PATH,
    EVAL_REPORT_PATH,
    MANUAL_EVAL_SHEET_PATH,
]

OVERCLAIM_BLOCKLIST = [
    "is security certified",
    "certified safe",
    "code correctness proven",
    "legal compliance is cleared",
    "privacy compliance is cleared",
    "license cleared for all use",
    "production ready",
    "quality guaranteed",
    "action authorized",
    "external action authorized",
]

PRIVATE_KERNEL_BLOCKLIST = [
    "ranking_weights:",
    "threshold_values:",
    "provider_priors:",
    "private_probe_seed:",
    "commercial_routing_policy:",
]

SECRET_BLOCKLIST = ["sk-", "ghp_", "hf_", "api_key=", "private key"]


def _artifact_text(paths: list[Path] = ARTIFACT_PATHS) -> str:
    chunks: list[str] = []
    for path in paths:
        if path.suffix == ".json":
            chunks.append(json.dumps(read_json(path) or read_list(path), ensure_ascii=False).lower())
        else:
            chunks.append(read_text(path).lower())
    return "\n".join(chunks)


def _guided_results_have_required_fields(results: list[dict[str, Any]]) -> bool:
    if not results:
        return False
    for item in results:
        for key in REQUIRED_GUIDED_KEYS:
            if not item.get(key):
                return False
    return True


def _all_hold_still_useful(results: list[dict[str, Any]]) -> bool:
    for item in results:
        candidates = item.get("top_candidates", [])
        if candidates and all(str(candidate.get("preliminary_route_decision", "")).startswith("HOLD") for candidate in candidates):
            if not item.get("next_action"):
                return False
    return True


def run_agent_discovery_3_gate(write_result: bool = True) -> dict[str, Any]:
    public_smoke = read_json(PUBLIC_DISCOVERY_SMOKE_PATH)
    pypi_smoke = read_json(PYPI_PUBLIC_INSTALL_SMOKE_PATH)
    registry_smoke = read_json(MCP_REGISTRY_PUBLIC_SMOKE_PATH)
    cases = read_list(EVAL_CASES_PATH)
    naive = read_list(NAIVE_BASELINE_PATH)
    guided = read_list(AOI_GUIDED_RESULTS_PATH)
    report = read_json(EVAL_REPORT_PATH)
    manual_sheet = read_text(MANUAL_EVAL_SHEET_PATH)
    text = _artifact_text()
    errors: list[str] = []
    warnings: list[str] = []

    missing = [str(path).replace("\\", "/") for path in ARTIFACT_PATHS if not (Path(__file__).resolve().parents[3] / path).exists()]
    if missing:
        warnings.append(f"Missing artifacts: {', '.join(missing)}")
    if any(term in text for term in SECRET_BLOCKLIST):
        errors.append("Token-like or secret-like content detected in discovery eval artifacts.")
    if any(term in text for term in PRIVATE_KERNEL_BLOCKLIST):
        errors.append("Private kernel implementation detail appears to be exposed.")
    if any(term in text for term in OVERCLAIM_BLOCKLIST):
        errors.append("Blocked overclaim phrase detected.")
    if not _guided_results_have_required_fields(guided) or not _all_hold_still_useful(guided):
        errors.append("AOI-guided eval is missing critical agent output fields or useful all-HOLD next actions.")
    if "do not upload private data" not in manual_sheet.lower() or "tokens" not in manual_sheet.lower():
        warnings.append("Manual eval sheet is missing expected no-private-data or token warning.")

    if errors:
        if any("Private kernel" in error for error in errors):
            decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
        elif any("overclaim" in error.lower() for error in errors):
            decision = "BLOCK_OVERCLAIM"
        elif any("Token" in error for error in errors):
            decision = "BLOCK_SECRET_FINDING"
        else:
            decision = "BLOCK_AGENT_EVAL_MISSING_CRITICAL_FIELDS"
    elif pypi_smoke.get("decision") != "PASS_PYPI_PUBLIC_INSTALL_SMOKE":
        decision = "HOLD_PUBLIC_INSTALL_SMOKE"
        warnings.append(f"PyPI smoke is {pypi_smoke.get('decision')}.")
    elif registry_smoke.get("decision") == "HOLD_REGISTRY_PROPAGATION" or public_smoke.get("decision") == "HOLD_REGISTRY_PROPAGATION":
        decision = "HOLD_REGISTRY_PROPAGATION"
        warnings.append("Registry smoke is still in propagation HOLD.")
    elif missing:
        decision = "HOLD_MANUAL_LLM_EVAL_NOT_RUN"
    else:
        decision = "PASS_AGENT_PUBLIC_DISCOVERY_AND_PROMPT_EVAL_READY"

    result = {
        "schema": "AOI_AgentDiscovery3GateResult/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "public_discovery_smoke_decision": public_smoke.get("decision"),
        "pypi_public_install_smoke_decision": pypi_smoke.get("decision"),
        "mcp_registry_public_smoke_decision": registry_smoke.get("decision"),
        "case_count": len(cases),
        "naive_result_count": len(naive),
        "aoi_guided_result_count": len(guided),
        "aoi_guided_total_score": report.get("aoi_guided_total_score"),
        "naive_total_score": report.get("naive_total_score"),
        "critical_fields_present": _guided_results_have_required_fields(guided),
        "all_hold_cases_useful": _all_hold_still_useful(guided),
        "token_printed": False,
        "external_llm_api_called": False,
        "posting_or_outreach_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(GATE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_agent_discovery_3_gate()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"agent_discovery_3_gate: {result['decision']}")


if __name__ == "__main__":
    main()
