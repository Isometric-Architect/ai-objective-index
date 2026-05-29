from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


@dataclass(frozen=True)
class VerticalConfig:
    vertical_id: str
    name: str
    scope: str
    reviewed_object: str
    input_type: str
    check_type: str
    receipt_path: Path
    gate_path: Path
    redaction_path: Path
    feedback_memory_path: Path
    primary_decision_field: str


VERTICALS: dict[str, VerticalConfig] = {
    "agentsec": VerticalConfig(
        vertical_id="agentsec",
        name="AgentSec Gate",
        scope="local/offline MCP or tool manifest review",
        reviewed_object="tool or MCP manifest metadata",
        input_type="manifest fixture",
        check_type="metadata permission and forbidden-action review",
        receipt_path=Path("pilot_receipts") / "agentsec" / "AGENTSEC_PILOT_RECEIPT_SAMPLE.json",
        gate_path=Path("public_launch") / "roe8" / "ROE8_AGENTSEC_PILOT_GATE_RESULT.json",
        redaction_path=Path("pilot_receipts") / "agentsec" / "AGENTSEC_PILOT_REDACTION_REPORT.json",
        feedback_memory_path=Path("pilot_receipts") / "agentsec" / "AGENTSEC_PILOT_FEEDBACK_MEMORY_ENTRY.json",
        primary_decision_field="agentsec_decision",
    ),
    "qira": VerticalConfig(
        vertical_id="qira",
        name="QIRA-Code ReleaseGate",
        scope="local/offline code-change release-gate review",
        reviewed_object="task packet and patch fixture",
        input_type="sample patch fixture",
        check_type="patch classification, behavior contract, and CI evidence intake",
        receipt_path=Path("pilot_receipts") / "qira" / "QIRA_PILOT_RECEIPT_SAMPLE.json",
        gate_path=Path("public_launch") / "roe9" / "ROE9_QIRA_PILOT_GATE_RESULT.json",
        redaction_path=Path("pilot_receipts") / "qira" / "QIRA_PILOT_REDACTION_REPORT.json",
        feedback_memory_path=Path("pilot_receipts") / "qira" / "QIRA_PILOT_FEEDBACK_MEMORY_ENTRY.json",
        primary_decision_field="release_gate_decision",
    ),
    "datacapsule": VerticalConfig(
        vertical_id="datacapsule",
        name="DataCapsule / AIDREG Engine",
        scope="local/offline corpus manifest review",
        reviewed_object="corpus manifest metadata",
        input_type="sample corpus manifest fixture",
        check_type="source-rights, privacy-risk, evaluation-boundary, and use-boundary review",
        receipt_path=Path("pilot_receipts") / "datacapsule" / "DATACAPSULE_PILOT_RECEIPT_SAMPLE.json",
        gate_path=Path("public_launch") / "roe10" / "ROE10_DATACAPSULE_PILOT_GATE_RESULT.json",
        redaction_path=Path("pilot_receipts") / "datacapsule" / "DATACAPSULE_PILOT_REDACTION_REPORT.json",
        feedback_memory_path=Path("pilot_receipts") / "datacapsule" / "DATACAPSULE_PILOT_FEEDBACK_MEMORY_ENTRY.json",
        primary_decision_field="capsule_decision",
    ),
}


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _to_repo_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _decision_summary(receipt: dict[str, Any]) -> dict[str, int]:
    summary = receipt.get("decision_summary")
    if isinstance(summary, dict):
        return {
            "allow_count": int(summary.get("allow_count", 0) or 0),
            "hold_count": int(summary.get("hold_count", 0) or 0),
            "block_count": int(summary.get("block_count", 0) or 0),
        }
    return {"allow_count": 0, "hold_count": 0, "block_count": 0}


def _primary_decision(config: VerticalConfig, receipt: dict[str, Any]) -> str:
    value = receipt.get(config.primary_decision_field)
    if isinstance(value, str) and value:
        return value
    findings = receipt.get("findings")
    if isinstance(findings, list):
        categories = {str(item.get("category", "")) for item in findings if isinstance(item, dict)}
        if "forbidden_action" in categories:
            return "BLOCK_FORBIDDEN_ACTION"
        if "release_side_effect" in categories:
            return "BLOCK_RELEASE_SIDE_EFFECT"
        if "act_boundary" in categories:
            return "BLOCK_ACTION_USE"
    summary = _decision_summary(receipt)
    if summary["block_count"]:
        return "BLOCK_REVIEW_REQUIRED"
    if summary["hold_count"]:
        return "HOLD_REVIEW_REQUIRED"
    return "ALLOW_REVIEW_ARTIFACT"


def _top_reasons(receipt: dict[str, Any], key: str) -> list[str]:
    summary = receipt.get("decision_summary")
    if not isinstance(summary, dict):
        return []
    reasons = summary.get(key)
    if not isinstance(reasons, list):
        return []
    return [str(reason) for reason in reasons if str(reason).strip()][:10]


def _external_action_used(receipt: dict[str, Any]) -> bool:
    risky_flags = [
        "external_actions_performed",
        "github_api_used",
        "live_mcp_called",
        "external_tool_executed",
        "external_repo_modified",
        "merge_performed",
        "deploy_performed",
        "publish_performed",
        "external_network_used",
        "crawler_used",
        "data_uploaded",
        "model_trained",
        "external_api_used",
    ]
    return any(bool(receipt.get(flag, False)) for flag in risky_flags)


def _live_execution_used(receipt: dict[str, Any]) -> bool:
    flags = ["live_mcp_called", "external_tool_executed", "merge_performed", "deploy_performed", "publish_performed", "model_trained"]
    return any(bool(receipt.get(flag, False)) for flag in flags)


def _redaction_status(redaction: dict[str, Any]) -> str:
    return str(redaction.get("decision", "UNKNOWN"))


def load_vertical_receipt(vertical_id: str) -> dict[str, Any]:
    config = VERTICALS[vertical_id]
    receipt = _read_json(config.receipt_path)
    gate = _read_json(config.gate_path)
    redaction = _read_json(config.redaction_path)
    feedback_memory = _read_json(config.feedback_memory_path)
    missing_receipt = not bool(receipt)
    summary = _decision_summary(receipt)
    return {
        "vertical_id": config.vertical_id,
        "name": config.name,
        "scope": config.scope,
        "reviewed_object": config.reviewed_object,
        "input_type": config.input_type,
        "check_type": config.check_type,
        "receipt_path": _to_repo_path(config.receipt_path),
        "gate_path": _to_repo_path(config.gate_path),
        "redaction_path": _to_repo_path(config.redaction_path),
        "feedback_memory_path": _to_repo_path(config.feedback_memory_path),
        "missing_receipt": missing_receipt,
        "receipt": receipt,
        "gate": gate,
        "redaction": redaction,
        "feedback_memory": feedback_memory,
        "allow_count": summary["allow_count"],
        "hold_count": summary["hold_count"],
        "block_count": summary["block_count"],
        "primary_decision": "HOLD_MISSING_RECEIPT" if missing_receipt else _primary_decision(config, receipt),
        "gate_result": str(gate.get("decision", "HOLD_GATE_NOT_FOUND")),
        "redaction_status": _redaction_status(redaction),
        "feedback_memory_status": str(feedback_memory.get("feedback_status", "unknown")),
        "top_hold_reasons": _top_reasons(receipt, "top_hold_reasons"),
        "top_block_reasons": _top_reasons(receipt, "top_block_reasons"),
        "no_external_action": not _external_action_used(receipt),
        "external_action_used": _external_action_used(receipt),
        "live_execution_used": _live_execution_used(receipt),
        "key_next_actions": [str(item) for item in feedback_memory.get("follow_up_actions", []) if str(item).strip()][:5]
        if isinstance(feedback_memory.get("follow_up_actions"), list)
        else [],
    }


def load_agentsec_receipt() -> dict[str, Any]:
    return load_vertical_receipt("agentsec")


def load_qira_receipt() -> dict[str, Any]:
    return load_vertical_receipt("qira")


def load_datacapsule_receipt() -> dict[str, Any]:
    return load_vertical_receipt("datacapsule")


def load_all_pilot_receipts() -> dict[str, Any]:
    verticals = [load_vertical_receipt(vertical_id) for vertical_id in ("agentsec", "qira", "datacapsule")]
    return {
        "vertical_count": len(verticals),
        "verticals": verticals,
        "missing_verticals": [vertical["vertical_id"] for vertical in verticals if vertical["missing_receipt"]],
        "external_action_used": any(vertical["external_action_used"] for vertical in verticals),
        "live_execution_used": any(vertical["live_execution_used"] for vertical in verticals),
    }
