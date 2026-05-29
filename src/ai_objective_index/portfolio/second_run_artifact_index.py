from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


ARTIFACT_INDEX_PATH = Path("pilot_second_runs") / "ROE15_SECOND_RUN_ARTIFACT_INDEX.json"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_artifact(path: Path) -> tuple[str, str, str]:
    name = path.name.lower()
    if "agentsec" in name:
        vertical = "agentsec"
    elif "qira" in name:
        vertical = "qira"
    elif "datacapsule" in name:
        vertical = "datacapsule"
    else:
        vertical = "portfolio"
    if "delta" in name:
        artifact_type = "second_run_delta"
    elif "result" in name:
        artifact_type = "second_run_result"
    elif "receipt" in name:
        artifact_type = "second_run_receipt"
    elif "memory" in name:
        artifact_type = "feedback_memory"
    elif "readout" in name:
        artifact_type = "reviewer_readout"
    elif "redaction" in name:
        artifact_type = "redaction_report"
    elif "known_limits" in name:
        artifact_type = "known_limits"
    else:
        artifact_type = "artifact"
    return vertical, artifact_type, "public-safe local/sample artifact"


def build_second_run_artifact_index(paths: list[Path], write_result: bool = True) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    root = _repo_root()
    for path in paths:
        full = root / path
        if not full.exists() or not full.is_file():
            continue
        vertical, artifact_type, reason = classify_artifact(path)
        entries.append(
            {
                "path": str(path).replace("\\", "/"),
                "artifact_type": artifact_type,
                "vertical": vertical,
                "generated_at": _timestamp(),
                "sha256": _sha256(full),
                "safe_to_share_publicly": True,
                "reason": reason,
            }
        )
    result = {
        "schema": "ResidualOps_SecondRunArtifactIndex/v0.1",
        "generated_at": _timestamp(),
        "artifact_count": len(entries),
        "artifacts": entries,
        "external_actions_performed": False,
        "token_printed": False,
    }
    if write_result:
        destination = root / ARTIFACT_INDEX_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
