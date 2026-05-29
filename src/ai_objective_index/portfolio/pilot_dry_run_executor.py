from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .agentsec_pilot_packager import package_agentsec_pilot
from .datacapsule_pilot_packager import package_datacapsule_pilot
from .pilot_dry_run_receipt import PilotDryRunResult, to_jsonable
from .pilot_vertical_router import PilotVerticalRoute
from .qira_pilot_packager import package_qira_pilot
from .roe10_datacapsule_pilot_gate import run_roe10_gate
from .roe8_agentsec_pilot_gate import run_roe8_gate
from .roe9_qira_pilot_gate import run_roe9_gate


DRY_RUN_DIR = Path("pilot_dry_runs")
AGENTSEC_RESULT_PATH = DRY_RUN_DIR / "ROE13_PILOT_DRY_RUN_RESULT_AGENTSEC.json"
QIRA_RESULT_PATH = DRY_RUN_DIR / "ROE13_PILOT_DRY_RUN_RESULT_QIRA.json"
DATACAPSULE_RESULT_PATH = DRY_RUN_DIR / "ROE13_PILOT_DRY_RUN_RESULT_DATACAPSULE.json"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _primary_agentsec_decision(receipt: dict[str, Any]) -> str:
    if receipt.get("decision_summary", {}).get("block_count", 0):
        categories = [finding.get("category") for finding in receipt.get("findings", []) if finding.get("decision") == "BLOCK"]
        if "forbidden_action" in categories:
            return "BLOCK_FORBIDDEN_ACTION"
        if "unsupported_claim" in categories:
            return "BLOCK_UNSUPPORTED_CLAIM"
        return "BLOCK_POLICY_RISK"
    if receipt.get("decision_summary", {}).get("hold_count", 0):
        return "HOLD_REVIEW_REQUIRED"
    return "ALLOW_METADATA_ONLY"


def _result_from_packaged(
    dry_run_id: str,
    vertical: str,
    intake_id: str,
    packaged: dict[str, Any],
    gate: dict[str, Any],
    selected_packager: str,
) -> PilotDryRunResult:
    receipt = packaged["receipt"]
    summary = receipt.get("decision_summary", {})
    if vertical == "agentsec":
        primary = _primary_agentsec_decision(receipt)
    elif vertical == "qira":
        primary = receipt.get("release_gate_decision", "UNKNOWN")
    else:
        primary = receipt.get("capsule_decision", "UNKNOWN")
    return PilotDryRunResult(
        dry_run_id=dry_run_id,
        vertical=vertical,  # type: ignore[arg-type]
        intake_id=intake_id,
        selected_packager=selected_packager,
        receipt_path=packaged["paths"]["receipt"],
        gate_result=gate.get("decision", "UNKNOWN"),
        allow_count=int(summary.get("allow_count", 0) or 0),
        hold_count=int(summary.get("hold_count", 0) or 0),
        block_count=int(summary.get("block_count", 0) or 0),
        primary_decision=primary,
        redaction_status=packaged.get("redaction", {}).get("decision", "UNKNOWN"),
        feedback_memory_status=packaged.get("feedback_memory", {}).get("feedback_status", "pending"),
        known_limits=receipt.get("feedback_memory", {}).get("known_limits", []),
        claim_boundary=receipt.get("claim_boundary", {}),
        external_action_used=bool(
            packaged.get("external_actions_performed", False)
            or packaged.get("external_api_used", False)
            or packaged.get("github_api_used", False)
            or packaged.get("external_repo_modified", False)
            or packaged.get("data_uploaded", False)
            or packaged.get("model_trained", False)
        ),
        token_printed=bool(packaged.get("token_printed", False)),
    )


def execute_vertical_dry_run(dry_run_id: str, vertical: str, route: PilotVerticalRoute) -> PilotDryRunResult:
    if route.selected_vertical != vertical or not route.can_generate_pilot_receipt:
        raise ValueError(f"route for {vertical} is not executable: {route.selected_vertical}")
    if vertical == "agentsec":
        packaged = package_agentsec_pilot(sample=True)
        gate = run_roe8_gate(write_result=True, ensure_sample=False)
        result = _result_from_packaged(dry_run_id, vertical, route.intake_id, packaged, gate, "package_agentsec_pilot")
        _write_json(AGENTSEC_RESULT_PATH, to_jsonable(result))
        return result
    if vertical == "qira":
        packaged = package_qira_pilot(sample=True)
        gate = run_roe9_gate(write_result=True, ensure_sample=False)
        result = _result_from_packaged(dry_run_id, vertical, route.intake_id, packaged, gate, "package_qira_pilot")
        _write_json(QIRA_RESULT_PATH, to_jsonable(result))
        return result
    if vertical == "datacapsule":
        packaged = package_datacapsule_pilot(sample=True)
        gate = run_roe10_gate(write_result=True, ensure_sample=False)
        result = _result_from_packaged(dry_run_id, vertical, route.intake_id, packaged, gate, "package_datacapsule_pilot")
        _write_json(DATACAPSULE_RESULT_PATH, to_jsonable(result))
        return result
    raise ValueError(f"unknown vertical: {vertical}")


def execute_all_verticals(dry_run_id: str, routes: dict[str, PilotVerticalRoute]) -> list[PilotDryRunResult]:
    results: list[PilotDryRunResult] = []
    for vertical in ["agentsec", "qira", "datacapsule"]:
        if vertical in routes:
            results.append(execute_vertical_dry_run(dry_run_id, vertical, routes[vertical]))
    return results
