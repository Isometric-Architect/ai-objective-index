from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_refresh_manifest import SHARE_V2_DIR, sha256_file, timestamp
from .external_share_refresh_redaction import scan_refresh_share_artifacts


ARCHIVE_V2_PATH = SHARE_V2_DIR / "ResidualOps_External_Safe_Demo_Pack_v2.zip"
ARCHIVE_RESULT_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_ARCHIVE_RESULT_V2.json"


def _safe_artifact_paths() -> list[Path]:
    root = _repo_root()
    paths: list[Path] = []
    for full in sorted((root / SHARE_V2_DIR).glob("*")):
        if not full.is_file() or full.suffix.lower() == ".zip":
            continue
        paths.append(full.relative_to(root))
    return paths


def run_refresh_archive(dry_run: bool = True, build: bool = False, write_result: bool = True) -> dict[str, Any]:
    paths = _safe_artifact_paths()
    redaction = scan_refresh_share_artifacts(paths, write_result=False)
    archive_built = False
    archive_checksum = ""
    errors: list[str] = []
    if build and not write_result:
        errors.append("archive build skipped because write_result=False")
    elif build and redaction["decision"] == "PASS_REDACTED":
        destination = _repo_root() / ARCHIVE_V2_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in paths:
                archive.write(_repo_root() / path, arcname=str(path.relative_to(SHARE_V2_DIR)).replace("\\", "/"))
        archive_built = True
        archive_checksum = sha256_file(destination)
    elif build:
        errors.append("redaction did not pass; archive not built")
    result = {
        "schema": "ResidualOps_ExternalShareRefreshArchiveResult/v0.1",
        "generated_at": timestamp(),
        "dry_run": dry_run,
        "build_requested": build,
        "archive_built": archive_built,
        "archive_path": str(ARCHIVE_V2_PATH).replace("\\", "/") if archive_built else "",
        "archive_sha256": archive_checksum,
        "included_file_count": len(paths),
        "redaction_decision": redaction["decision"],
        "result_token": "DRY_RUN_ONLY" if dry_run and not build else "ARCHIVE_BUILT" if archive_built else "HOLD_ARCHIVE_NOT_BUILT",
        "errors": errors,
        "warnings": ["archive is optional; share only when the V2 claim ceiling remains visible"] if not archive_built else [],
    }
    if write_result:
        destination = _repo_root() / ARCHIVE_RESULT_V2_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build or dry-run the ROE-22 refreshed external-safe share archive.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--build", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_refresh_archive(dry_run=not args.build, build=args.build, write_result=not args.no_write)
    print(f"external_share_refresh_archive: {result['result_token']} archive_built={result['archive_built']}")


if __name__ == "__main__":
    main()
