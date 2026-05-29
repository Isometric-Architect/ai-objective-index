from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .residualops_portfolio_loader import load_all_pilot_receipts


MATRIX_JSON_PATH = Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_VERTICAL_COMPARISON_MATRIX.json"
MATRIX_MD_PATH = Path("pilot_receipts") / "portfolio" / "RESIDUALOPS_VERTICAL_COMPARISON_MATRIX.md"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def _claim_boundary_for(vertical_id: str) -> str:
    if vertical_id == "agentsec":
        return "not security certification; not compliance audit; no external action authorization"
    if vertical_id == "qira":
        return "not code correctness proof; not security certification; no merge/deploy authorization"
    return "not legal/privacy/license/evaluation proof; no training/action authorization"


def build_vertical_matrix(loaded: dict[str, Any] | None = None) -> dict[str, Any]:
    loaded = loaded or load_all_pilot_receipts()
    rows = []
    for vertical in loaded["verticals"]:
        hold_reasons = vertical.get("top_hold_reasons", [])
        block_reasons = vertical.get("top_block_reasons", [])
        rows.append(
            {
                "vertical": vertical["name"],
                "vertical_id": vertical["vertical_id"],
                "reviewed_object": vertical["reviewed_object"],
                "input_type": vertical["input_type"],
                "check_type": vertical["check_type"],
                "external_action_used": vertical["external_action_used"],
                "live_execution_used": vertical["live_execution_used"],
                "allow_count": vertical["allow_count"],
                "hold_count": vertical["hold_count"],
                "block_count": vertical["block_count"],
                "primary_block_or_hold_reason": (block_reasons or hold_reasons or ["none"])[0],
                "feedback_memory_status": vertical["feedback_memory_status"],
                "claim_boundary": _claim_boundary_for(vertical["vertical_id"]),
                "next_action": (vertical.get("key_next_actions") or ["review next owner-consented pilot path"])[0],
            }
        )
    return {
        "schema": "ResidualOps_VerticalComparisonMatrix/v0.1",
        "generated_at": _timestamp(),
        "row_count": len(rows),
        "rows": rows,
        "external_action_used": any(row["external_action_used"] for row in rows),
        "live_execution_used": any(row["live_execution_used"] for row in rows),
    }


def matrix_to_markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# ResidualOps Vertical Comparison Matrix",
        "",
        "| Vertical | Reviewed object | Check type | ALLOW | HOLD | BLOCK | Primary reason | Feedback |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in matrix["rows"]:
        lines.append(
            "| {vertical} | {reviewed_object} | {check_type} | `{allow_count}` | `{hold_count}` | `{block_count}` | {reason} | `{feedback}` |".format(
                vertical=row["vertical"],
                reviewed_object=row["reviewed_object"],
                check_type=row["check_type"],
                allow_count=row["allow_count"],
                hold_count=row["hold_count"],
                block_count=row["block_count"],
                reason=row["primary_block_or_hold_reason"],
                feedback=row["feedback_memory_status"],
            )
        )
    lines.extend(
        [
            "",
            "All rows are local/offline receipt artifacts. The matrix is not a security certification, code correctness proof, legal/privacy/license/evaluation proof, quality guarantee, product-readiness claim, or external action authorization.",
            "",
        ]
    )
    return "\n".join(lines)


def write_vertical_matrix(loaded: dict[str, Any] | None = None) -> dict[str, Any]:
    matrix = build_vertical_matrix(loaded)
    _write_json(MATRIX_JSON_PATH, matrix)
    _write_text(MATRIX_MD_PATH, matrix_to_markdown(matrix))
    return matrix
