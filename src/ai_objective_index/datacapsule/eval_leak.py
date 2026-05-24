from __future__ import annotations

from typing import Any

from .models import EvalLeakSeparationReport


def _purposes(row: dict[str, Any]) -> set[str]:
    value = row.get("purpose", [])
    if isinstance(value, str):
        parts = [item.strip() for item in value.replace(";", ",").split(",")]
        return {item for item in parts if item}
    if isinstance(value, list):
        return {str(item).strip() for item in value if str(item).strip()}
    return set()


def build_eval_leak_separation_report(manifest: dict[str, Any]) -> EvalLeakSeparationReport:
    files = manifest.get("files") if isinstance(manifest.get("files"), list) else []
    train_paths: set[str] = set()
    eval_paths: set[str] = set()
    missing_purpose: list[str] = []
    flagged: list[str] = []

    for item in files:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "").strip()
        if not path:
            continue
        purposes = _purposes(item)
        if not purposes:
            missing_purpose.append(path)
        if "train" in purposes:
            train_paths.add(path)
        if "evaluate" in purposes or "eval" in purposes:
            eval_paths.add(path)
        flags = item.get("risk_flags") if isinstance(item.get("risk_flags"), dict) else {}
        if flags.get("eval_leak"):
            flagged.append(path)

    overlap = sorted(train_paths & eval_paths)
    hold_reasons: list[str] = []
    if missing_purpose:
        hold_reasons.append("one or more manifest rows do not declare purpose")
    if flagged:
        hold_reasons.append("one or more manifest rows explicitly mark eval_leak risk")
    if overlap:
        return EvalLeakSeparationReport(
            decision="BLOCK_EVAL_LEAK_CONFLICT",
            train_count=len(train_paths),
            eval_count=len(eval_paths),
            overlap_count=len(overlap),
            overlap_paths=overlap,
            hold_reasons=hold_reasons + ["same local path appears in both train and evaluation purposes"],
        )
    if hold_reasons:
        return EvalLeakSeparationReport(
            decision="HOLD_EVAL_LEAK_REVIEW",
            train_count=len(train_paths),
            eval_count=len(eval_paths),
            overlap_count=0,
            hold_reasons=hold_reasons,
        )
    return EvalLeakSeparationReport(
        decision="PASS_EVAL_SEPARATION_LOCAL_METADATA",
        train_count=len(train_paths),
        eval_count=len(eval_paths),
        overlap_count=0,
    )
