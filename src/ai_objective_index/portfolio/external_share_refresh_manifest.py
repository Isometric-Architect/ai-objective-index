from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


SHARE_V2_DIR = Path("external_share_pack_v2")
MANIFEST_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_MANIFEST_V2.json"


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_refresh_artifact(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".html"):
        return "static_html_demo_v2"
    if "readme" in name:
        return "external_safe_readme_v2"
    if "dashboard" in name:
        return "redacted_dashboard_v2"
    if "status_cards" in name:
        return "status_cards_v2"
    if "timeline" in name:
        return "timeline_v2"
    if "feedback_memory" in name:
        return "feedback_memory_v2"
    if "claim" in name:
        return "claim_boundary_or_audit_v2"
    if "script" in name:
        return "operator_script_v2"
    if "delta" in name:
        return "refresh_delta_v2"
    if "manifest" in name:
        return "manifest_v2"
    if "checksum" in name:
        return "checksums_v2"
    if "redaction" in name:
        return "redaction_report_v2"
    if "distribution" in name:
        return "distribution_boundary_v2"
    return "external_safe_artifact_v2"


def build_refresh_manifest(paths: list[Path], source_map: dict[str, str] | None = None, write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    source_map = source_map or {}
    artifacts: list[dict[str, Any]] = []
    for path in paths:
        full = root / path
        if not full.exists() or not full.is_file():
            continue
        rel = str(path).replace("\\", "/")
        artifacts.append(
            {
                "path": rel,
                "size": full.stat().st_size,
                "sha256": sha256_file(full),
                "source_path": source_map.get(rel, ""),
                "artifact_type": classify_refresh_artifact(path),
                "safe_to_share_publicly": True,
                "reason": "redacted static local V2 demo artifact with visible claim ceiling and skipped/HOLD status preserved",
            }
        )
    manifest = {
        "schema": "ResidualOps_ExternalShareRefreshManifest/v0.1",
        "generated_at": timestamp(),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "external_actions_performed": False,
        "network_used": False,
        "token_printed": False,
    }
    if write_result:
        destination = root / MANIFEST_V2_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest
