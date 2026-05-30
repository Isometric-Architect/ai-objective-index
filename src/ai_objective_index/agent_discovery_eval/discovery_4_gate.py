from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import (
    AGENT_OPERATOR_POSITIONING_PATH,
    CAPABILITY_DECISION_PACKET_DRAFT_PATH,
    CLAUDE_FEEDBACK_PACKET_PATH,
    COMPETITIVE_SYNTHESIS_PATH,
    CROSS_MODEL_SUMMARY_PATH,
    DISCOVERY_4_GATE_PATH,
    DISCOVERY_4_NEXT_ACTIONS_PATH,
    DISCOVERY_4_SUMMARY_PATH,
    FRESHNESS_RUGPULL_NOTES_PATH,
    GEMINI_FEEDBACK_PACKET_PATH,
    GPT55_FEEDBACK_PACKET_PATH,
    HOLD_TO_REPLAN_SPEC_PATH,
    ROUTE_SEMANTICS_ROADMAP_PATH,
    TEST_RESIDUAL_RECONCILIATION_PATH,
    read_json,
    read_text,
    repo_root,
    timestamp,
    write_json,
)
from .competitive_feedback_synthesis import run_competitive_feedback_synthesis
from .cross_model_feedback_classifier import run_cross_model_feedback_classifier
from .manual_cross_model_intake import run_manual_cross_model_intake
from .test_residual_reconciliation import run_test_residual_reconciliation


ARTIFACT_PATHS = [
    GEMINI_FEEDBACK_PACKET_PATH,
    GPT55_FEEDBACK_PACKET_PATH,
    CLAUDE_FEEDBACK_PACKET_PATH,
    CROSS_MODEL_SUMMARY_PATH,
    COMPETITIVE_SYNTHESIS_PATH,
    ROUTE_SEMANTICS_ROADMAP_PATH,
    HOLD_TO_REPLAN_SPEC_PATH,
    CAPABILITY_DECISION_PACKET_DRAFT_PATH,
    AGENT_OPERATOR_POSITIONING_PATH,
    FRESHNESS_RUGPULL_NOTES_PATH,
    TEST_RESIDUAL_RECONCILIATION_PATH,
    DISCOVERY_4_SUMMARY_PATH,
    DISCOVERY_4_NEXT_ACTIONS_PATH,
]

SECRET_BLOCKLIST = ["sk-", "ghp_", "api_key=", "private key", "pypi-"]
PRIVATE_KERNEL_BLOCKLIST = [
    "ranking_weights:",
    "threshold_values:",
    "provider_priors:",
    "private_probe_seed:",
    "commercial_routing_policy:",
]
OVERCLAIM_BLOCKLIST = [
    "is security certified",
    "certified safe",
    "code correctness proven",
    "production ready",
    "quality guaranteed",
    "action authorized by aoi",
    "full suite green",
    "all tests passed globally",
]


def _artifact_text(paths: list[Path] = ARTIFACT_PATHS) -> str:
    chunks: list[str] = []
    for path in paths:
        full = repo_root() / path
        if not full.exists():
            continue
        if path.suffix == ".json":
            chunks.append(json.dumps(read_json(path), ensure_ascii=False).lower())
        else:
            chunks.append(read_text(path).lower())
    return "\n".join(chunks)


def _ensure_artifacts() -> None:
    run_manual_cross_model_intake(write_result=True)
    run_cross_model_feedback_classifier(write_result=True)
    run_competitive_feedback_synthesis(write_result=True)
    run_test_residual_reconciliation(write_result=True)


def run_discovery_4_gate(write_result: bool = True, ensure_artifacts: bool = True) -> dict[str, object]:
    if ensure_artifacts:
        _ensure_artifacts()
    root = repo_root()
    missing = [str(path).replace("\\", "/") for path in ARTIFACT_PATHS if not (root / path).exists()]
    summary = read_json(CROSS_MODEL_SUMMARY_PATH)
    residual = read_json(TEST_RESIDUAL_RECONCILIATION_PATH)
    text = _artifact_text()
    errors: list[str] = []
    warnings: list[str] = []

    if missing:
        warnings.append(f"Missing Discovery 4 artifacts: {', '.join(missing)}")
    if any(term in text for term in SECRET_BLOCKLIST):
        errors.append("Token-like or secret-like content detected.")
    if any(term in text for term in PRIVATE_KERNEL_BLOCKLIST):
        errors.append("Private kernel implementation detail appears to be exposed.")
    if any(term in text for term in OVERCLAIM_BLOCKLIST):
        errors.append("Blocked overclaim or false full-suite claim phrase detected.")
    if residual.get("full_suite_green_claim_allowed") is True:
        errors.append("Residual reconciliation allows a full-suite green claim without a known passing full run.")
    if summary.get("packet_count") != 3:
        warnings.append("Cross-model summary does not include all three model packets.")

    if errors:
        if any("Private kernel" in error for error in errors):
            decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
        elif any("Token" in error for error in errors):
            decision = "BLOCK_SECRET_FINDING"
        elif any("full-suite" in error or "overclaim" in error.lower() for error in errors):
            decision = "BLOCK_FALSE_FULL_SUITE_CLAIM" if "full-suite" in " ".join(errors) else "BLOCK_OVERCLAIM"
        else:
            decision = "BLOCK_OVERCLAIM"
    elif residual.get("decision") == "HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED":
        decision = "HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED"
    elif missing:
        decision = "HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED"
    else:
        decision = "PASS_CROSS_MODEL_FEEDBACK_INTAKE_READY"

    result = {
        "schema": "AOI_AgentDiscovery4GateResult/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "feedback_packet_count": summary.get("packet_count", 0),
        "cross_model_summary_present": bool(summary),
        "test_residual_decision": residual.get("decision"),
        "full_suite_green_claim_allowed": bool(residual.get("full_suite_green_claim_allowed")),
        "token_printed": False,
        "external_llm_api_called": False,
        "posting_or_outreach_performed": False,
        "pypi_upload_performed": False,
        "mcp_registry_publish_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(DISCOVERY_4_GATE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_discovery_4_gate(write_result=True)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"discovery_4_gate: {result['decision']}")


if __name__ == "__main__":
    main()
