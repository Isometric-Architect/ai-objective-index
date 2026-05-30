from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TARGET_VERSION = "0.3.0a2"
PACKAGE_NAME = "ai-objective-index"
CANONICAL_MCP_NAME = "io.github.Isometric-Architect/ai-objective-index"

OUTPUT_DIR = Path("agent_discovery_eval")
PUBLIC_DISCOVERY_SMOKE_PATH = OUTPUT_DIR / "PUBLIC_DISCOVERY_SMOKE_RESULT.json"
PYPI_PUBLIC_INSTALL_SMOKE_PATH = OUTPUT_DIR / "PYPI_PUBLIC_INSTALL_SMOKE_RESULT.json"
MCP_REGISTRY_PUBLIC_SMOKE_PATH = OUTPUT_DIR / "MCP_REGISTRY_PUBLIC_SMOKE_RESULT.json"
EVAL_CASES_PATH = OUTPUT_DIR / "ORDINARY_AGENT_EVAL_CASES.json"
NAIVE_BASELINE_PATH = OUTPUT_DIR / "ORDINARY_AGENT_NAIVE_BASELINE_RESULTS.json"
AOI_GUIDED_RESULTS_PATH = OUTPUT_DIR / "AOI_GUIDED_AGENT_RESULTS.json"
EVAL_REPORT_PATH = OUTPUT_DIR / "AGENT_PROMPT_EVAL_REPORT.json"
RUBRIC_PATH = OUTPUT_DIR / "AGENT_PROMPT_EVAL_RUBRIC.md"
MANUAL_EVAL_SHEET_PATH = OUTPUT_DIR / "MANUAL_CHATGPT_CLAUDE_GEMINI_EVAL_SHEET.md"
FAILURE_FIXTURES_PATH = OUTPUT_DIR / "ORDINARY_AGENT_FAILURE_FIXTURES.md"
GATE_PATH = OUTPUT_DIR / "AOI_AGENT_DISCOVERY_3_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "AOI_AGENT_DISCOVERY_3_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "AOI_AGENT_DISCOVERY_3_NEXT_ACTIONS.md"

MANUAL_CROSS_MODEL_DIR = OUTPUT_DIR / "manual_cross_model"
GEMINI_FEEDBACK_PACKET_PATH = MANUAL_CROSS_MODEL_DIR / "GEMINI_FEEDBACK_PACKET.json"
GPT55_FEEDBACK_PACKET_PATH = MANUAL_CROSS_MODEL_DIR / "GPT55_THINKING_FEEDBACK_PACKET.json"
CLAUDE_FEEDBACK_PACKET_PATH = MANUAL_CROSS_MODEL_DIR / "CLAUDE_OPUS48_FEEDBACK_PACKET.json"
CROSS_MODEL_SUMMARY_PATH = MANUAL_CROSS_MODEL_DIR / "CROSS_MODEL_FEEDBACK_SUMMARY.json"
COMPETITIVE_SYNTHESIS_PATH = MANUAL_CROSS_MODEL_DIR / "COMPETITIVE_FEEDBACK_SYNTHESIS.md"
ROUTE_SEMANTICS_ROADMAP_PATH = MANUAL_CROSS_MODEL_DIR / "ROUTE_SEMANTICS_ROADMAP.md"
HOLD_TO_REPLAN_SPEC_PATH = MANUAL_CROSS_MODEL_DIR / "HOLD_TO_REPLAN_LOOP_SPEC.md"
CAPABILITY_DECISION_PACKET_DRAFT_PATH = MANUAL_CROSS_MODEL_DIR / "CAPABILITY_DECISION_PACKET_DRAFT.md"
AGENT_OPERATOR_POSITIONING_PATH = MANUAL_CROSS_MODEL_DIR / "AGENT_OPERATOR_DUAL_POSITIONING.md"
FRESHNESS_RUGPULL_NOTES_PATH = MANUAL_CROSS_MODEL_DIR / "FRESHNESS_RUGPULL_NEGATIVE_CACHE_NOTES.md"
TEST_RESIDUAL_RECONCILIATION_PATH = MANUAL_CROSS_MODEL_DIR / "TEST_RESIDUAL_RECONCILIATION_RESULT.json"
DISCOVERY_4_GATE_PATH = MANUAL_CROSS_MODEL_DIR / "AOI_AGENT_DISCOVERY_4_GATE_RESULT.json"
DISCOVERY_4_SUMMARY_PATH = MANUAL_CROSS_MODEL_DIR / "AOI_AGENT_DISCOVERY_4_SUMMARY.md"
DISCOVERY_4_NEXT_ACTIONS_PATH = MANUAL_CROSS_MODEL_DIR / "AOI_AGENT_DISCOVERY_4_NEXT_ACTIONS.md"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> Path:
    destination = repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def read_json(path: Path) -> dict[str, Any]:
    full = repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def read_list(path: Path) -> list[dict[str, Any]]:
    full = repo_root() / path
    if not full.exists():
        return []
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return payload if isinstance(payload, list) else []


def write_text(path: Path, text: str) -> Path:
    destination = repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def read_text(path: Path) -> str:
    full = repo_root() / path
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")
