from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_pack_manifest import SHARE_DIR, sha256_file, timestamp


CHECKSUMS_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_CHECKSUMS.json"


def build_share_checksums(paths: list[Path], write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    checksums: dict[str, str] = {}
    for path in paths:
        full = root / path
        if full.exists() and full.is_file():
            checksums[str(path).replace("\\", "/")] = sha256_file(full)
    payload = {
        "schema": "ResidualOps_ExternalSafeSharePackChecksums/v0.1",
        "generated_at": timestamp(),
        "checksum_count": len(checksums),
        "checksums": checksums,
    }
    if write_result:
        destination = root / CHECKSUMS_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
