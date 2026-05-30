from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


SHARE_DIR = Path("external_share_pack")
MANIFEST_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_MANIFEST.json"


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_share_artifact(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".html"):
        return "static_html_demo"
    if "readme" in name:
        return "external_safe_readme"
    if "dashboard" in name:
        return "redacted_dashboard"
    if "claim" in name:
        return "claim_boundary"
    if "script" in name:
        return "operator_script"
    if "manifest" in name:
        return "manifest"
    if "checksum" in name:
        return "checksums"
    if "redaction" in name:
        return "redaction_report"
    if "distribution" in name:
        return "distribution_boundary"
    return "external_safe_artifact"


def build_share_manifest(paths: list[Path], source_map: dict[str, str] | None = None, write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    entries: list[dict[str, Any]] = []
    source_map = source_map or {}
    for path in paths:
        full = root / path
        if not full.exists() or not full.is_file():
            continue
        rel = str(path).replace("\\", "/")
        entries.append(
            {
                "path": rel,
                "size": full.stat().st_size,
                "sha256": sha256_file(full),
                "source_path": source_map.get(rel, ""),
                "artifact_type": classify_share_artifact(path),
                "safe_to_share_publicly": True,
                "reason": "redacted static local demo artifact with visible claim ceiling",
            }
        )
    manifest = {
        "schema": "ResidualOps_ExternalSafeSharePackManifest/v0.1",
        "generated_at": timestamp(),
        "artifact_count": len(entries),
        "artifacts": entries,
        "external_actions_performed": False,
        "network_used": False,
        "token_printed": False,
    }
    if write_result:
        destination = root / MANIFEST_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest
