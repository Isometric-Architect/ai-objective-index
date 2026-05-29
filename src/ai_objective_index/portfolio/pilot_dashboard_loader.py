from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


VERTICAL_RECEIPT_PATHS = {
    "agentsec": Path("pilot_receipts") / "agentsec" / "AGENTSEC_PILOT_RECEIPT_SAMPLE.json",
    "qira": Path("pilot_receipts") / "qira" / "QIRA_PILOT_RECEIPT_SAMPLE.json",
    "datacapsule": Path("pilot_receipts") / "datacapsule" / "DATACAPSULE_PILOT_RECEIPT_SAMPLE.json",
}

GATE_PATHS = {
    "agentsec_gate": Path("public_launch") / "roe8" / "ROE8_AGENTSEC_PILOT_GATE_RESULT.json",
    "qira_gate": Path("public_launch") / "roe9" / "ROE9_QIRA_PILOT_GATE_RESULT.json",
    "datacapsule_gate": Path("public_launch") / "roe10" / "ROE10_DATACAPSULE_PILOT_GATE_RESULT.json",
    "portfolio_gate": Path("public_launch") / "roe11" / "ROE11_UNIFIED_PORTFOLIO_GATE_RESULT.json",
    "intake_gate": Path("public_launch") / "roe12" / "ROE12_PILOT_INTAKE_GATE_RESULT.json",
    "dry_run_gate": Path("public_launch") / "roe13" / "ROE13_PILOT_DRY_RUN_GATE_RESULT.json",
    "feedback_gate": Path("public_launch") / "roe14" / "ROE14_FEEDBACK_SECOND_RUN_GATE_RESULT.json",
    "second_run_gate": Path("public_launch") / "roe15" / "ROE15_SECOND_RUN_GATE_RESULT.json",
}

EXPECTED_ARTIFACT_PATHS = {
    "portfolio": Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_UNIFIED_PILOT_PORTFOLIO.json",
    "dry_run": Path("pilot_dry_runs") / "ROE13_PILOT_DRY_RUN_RECEIPT.json",
    "feedback_plan": Path("pilot_feedback") / "PILOT_SECOND_RUN_PLAN_SAMPLE.json",
    "second_run": Path("pilot_second_runs") / "ROE15_SECOND_RUN_RECEIPT.json",
}

INTAKE_GLOB = Path("pilot_intake")


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _decision(payload: dict[str, Any]) -> str:
    return str(payload.get("decision") or payload.get("overall_token") or payload.get("result_token") or "HOLD_MISSING_ARTIFACT")


def _counts(receipt: dict[str, Any]) -> dict[str, int]:
    summary = receipt.get("decision_summary", {}) if isinstance(receipt, dict) else {}
    return {
        "allow_count": int(summary.get("allow_count", 0) or 0),
        "hold_count": int(summary.get("hold_count", 0) or 0),
        "block_count": int(summary.get("block_count", 0) or 0),
    }


def _primary_decision(vertical: str, receipt: dict[str, Any]) -> str:
    if vertical == "qira":
        return str(receipt.get("release_gate_decision") or receipt.get("patch_classification", {}).get("classification_decision") or "BLOCK_RELEASE_SIDE_EFFECT")
    if vertical == "datacapsule":
        return str(receipt.get("capsule_decision") or "BLOCK_ACTION_USE")
    return str(receipt.get("primary_decision") or "BLOCK_FORBIDDEN_ACTION")


def _reason(receipt: dict[str, Any], key: str) -> str:
    reasons = receipt.get("decision_summary", {}).get(key, [])
    if isinstance(reasons, list) and reasons:
        return str(reasons[0])
    return ""


def _redaction_for(vertical: str) -> str:
    paths = {
        "agentsec": Path("pilot_receipts") / "agentsec" / "AGENTSEC_PILOT_REDACTION_REPORT.json",
        "qira": Path("pilot_receipts") / "qira" / "QIRA_PILOT_REDACTION_REPORT.json",
        "datacapsule": Path("pilot_receipts") / "datacapsule" / "DATACAPSULE_PILOT_REDACTION_REPORT.json",
    }
    path = paths.get(vertical)
    if path is None:
        return "HOLD_MISSING_ARTIFACT"
    return _decision(_read_json(path))


def _feedback_status(vertical: str) -> str:
    memory = _read_json(Path("pilot_second_runs") / "ROE15_SECOND_RUN_FEEDBACK_MEMORY.json")
    for entry in memory.get("updated_entries", []):
        if isinstance(entry, dict) and vertical in str(entry.get("feedback_id", "")):
            return str(entry.get("new_status", "pending"))
    return "pending"


def _second_run_status(vertical: str) -> str:
    receipt = _read_json(Path("pilot_second_runs") / "ROE15_SECOND_RUN_RECEIPT.json")
    for result in receipt.get("vertical_results", []):
        if isinstance(result, dict) and result.get("vertical") == vertical:
            return str(result.get("plan_status", "READY_FOR_LOCAL_SECOND_RUN"))
    return "HOLD_MISSING_ARTIFACT"


def load_dashboard_sources() -> dict[str, Any]:
    root = _repo_root()
    missing: list[str] = []
    verticals: list[dict[str, Any]] = []
    for vertical, path in VERTICAL_RECEIPT_PATHS.items():
        receipt = _read_json(path)
        if not receipt:
            missing.append(str(path).replace("\\", "/"))
        counts = _counts(receipt)
        verticals.append(
            {
                "vertical": vertical,
                "receipt_path": str(path).replace("\\", "/"),
                "receipt": receipt,
                "allow_count": counts["allow_count"],
                "hold_count": counts["hold_count"],
                "block_count": counts["block_count"],
                "primary_decision": _primary_decision(vertical, receipt),
                "top_hold_reason": _reason(receipt, "top_hold_reasons"),
                "top_block_reason": _reason(receipt, "top_block_reasons"),
                "redaction_status": _redaction_for(vertical),
                "feedback_status": _feedback_status(vertical),
                "second_run_status": _second_run_status(vertical),
            }
        )

    gates: dict[str, str] = {}
    for name, path in GATE_PATHS.items():
        payload = _read_json(path)
        if not payload:
            missing.append(str(path).replace("\\", "/"))
        gates[name] = _decision(payload)

    artifacts: dict[str, dict[str, Any]] = {}
    for name, path in EXPECTED_ARTIFACT_PATHS.items():
        payload = _read_json(path)
        if not payload:
            missing.append(str(path).replace("\\", "/"))
        artifacts[name] = {"path": str(path).replace("\\", "/"), "payload": payload}

    intake_paths = sorted((root / INTAKE_GLOB).glob("*.json")) if (root / INTAKE_GLOB).exists() else []
    if not intake_paths:
        missing.append("pilot_intake/*.json")
    artifacts["intake"] = {
        "paths": [str(path.relative_to(root)).replace("\\", "/") for path in intake_paths],
        "count": len(intake_paths),
    }

    second_run = artifacts["second_run"]["payload"]
    dry_run = artifacts["dry_run"]["payload"]
    return {
        "verticals": verticals,
        "gates": gates,
        "artifacts": artifacts,
        "missing_artifacts": sorted(set(missing)),
        "dry_run": dry_run,
        "second_run": second_run,
        "external_action_count": int(second_run.get("aggregate_summary", {}).get("external_action_count", 0) or dry_run.get("aggregate_summary", {}).get("external_action_count", 0) or 0),
        "network_used": False,
        "github_api_used": False,
        "raw_private_data_inspected": False,
    }
