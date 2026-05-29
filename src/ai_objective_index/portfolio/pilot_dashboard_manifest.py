from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


MANIFEST_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD_MANIFEST.json"
CHECKSUMS_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD_CHECKSUMS.json"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_dashboard_artifact(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    if "dashboard" in name:
        artifact_type = "dashboard"
    elif "status_cards" in name:
        artifact_type = "status_cards"
    elif "timeline" in name:
        artifact_type = "timeline"
    elif "claim_boundary" in name:
        artifact_type = "claim_boundary"
    elif "redaction" in name:
        artifact_type = "redaction_report"
    elif "known_limits" in name:
        artifact_type = "known_limits"
    elif "checksum" in name:
        artifact_type = "checksums"
    else:
        artifact_type = "artifact"
    return artifact_type, "static local dashboard artifact with claim boundaries"


def build_dashboard_manifest(paths: list[Path], write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    artifacts: list[dict[str, Any]] = []
    checksums: dict[str, str] = {}
    for path in paths:
        full = root / path
        if not full.exists() or not full.is_file():
            continue
        digest = _sha256(full)
        artifact_type, reason = classify_dashboard_artifact(path)
        rel = str(path).replace("\\", "/")
        artifacts.append(
            {
                "path": rel,
                "artifact_type": artifact_type,
                "sha256": digest,
                "bytes": full.stat().st_size,
                "generated_at": _timestamp(),
                "safe_to_share_publicly": True,
                "reason": reason,
            }
        )
        checksums[rel] = digest
    manifest = {
        "schema": "ResidualOps_PilotDashboardManifest/v0.1",
        "generated_at": _timestamp(),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "external_actions_performed": False,
        "token_printed": False,
    }
    checksum_payload = {
        "schema": "ResidualOps_PilotDashboardChecksums/v0.1",
        "generated_at": _timestamp(),
        "checksum_count": len(checksums),
        "checksums": checksums,
    }
    if write_result:
        (root / MANIFEST_PATH).parent.mkdir(parents=True, exist_ok=True)
        (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (root / CHECKSUMS_PATH).write_text(json.dumps(checksum_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"manifest": manifest, "checksums": checksum_payload}
