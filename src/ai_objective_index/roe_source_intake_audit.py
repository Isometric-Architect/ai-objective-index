from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "roe0" / "ROE_SOURCE_INTAKE_AUDIT.json"
QBCPL_ZIP = "QBCPL_RUN019_INTERNAL_SOURCE_MASTER_INTEGRATION_bundle_v0_1.zip"
RESIDUALOPS_FOLDERS = ["RdsidualOps_Engine", "ResidualOps_Engine"]
QBCPL_EXTRACT_PREFIX = "data/generated/qbcpl_run019_extract_for_analysis_"


def _write_json(path: Path, payload: dict[str, Any], root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_ls_files(root: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-c", "safe.directory=C:/Users/Isometric-Architect/Desktop/ai_objective_index", "ls-files"],
            cwd=root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return []
    if completed.returncode != 0:
        return []
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def _zip_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    entry_sizes: list[int] = []
    try:
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                entry_sizes.append(info.file_size)
    except (OSError, zipfile.BadZipFile) as exc:
        return {
            "exists": True,
            "readable": False,
            "size_bytes": path.stat().st_size,
            "sha256": _sha256(path),
            "error": str(exc),
        }
    return {
        "exists": True,
        "readable": True,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "entry_count": len(entry_sizes),
        "entry_names_redacted": True,
        "entry_sizes": entry_sizes,
    }


def _folder_summary(root: Path, folder_name: str) -> dict[str, Any]:
    folder = root / folder_name
    if not folder.exists() or not folder.is_dir():
        return {"name": folder_name, "exists": False}
    files = [item for item in folder.rglob("*") if item.is_file()]
    suffix_counts: dict[str, int] = {}
    for item in files:
        suffix_counts[item.suffix.lower() or "<none>"] = suffix_counts.get(item.suffix.lower() or "<none>", 0) + 1
    return {
        "name": folder_name,
        "exists": True,
        "file_count": len(files),
        "suffix_counts": suffix_counts,
        "sample_file_names_redacted": True,
    }


def _tracked_internal_source_findings(git_files: Iterable[str]) -> list[str]:
    findings: list[str] = []
    for raw in git_files:
        normalized = raw.replace("\\", "/")
        lowered = normalized.lower()
        if normalized == QBCPL_ZIP:
            findings.append(normalized)
        if lowered.startswith("rdsidualops_engine/") or lowered.startswith("residualops_engine/"):
            findings.append(normalized)
        if lowered.startswith(QBCPL_EXTRACT_PREFIX.lower()):
            findings.append(normalized)
    return findings


def run_source_intake_audit(
    write_result: bool = True,
    root: Path | None = None,
    git_files: Iterable[str] | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    tracked_files = list(git_files) if git_files is not None else _git_ls_files(base)
    zip_info = _zip_summary(base / QBCPL_ZIP)
    residualops_info = [_folder_summary(base, folder) for folder in RESIDUALOPS_FOLDERS]
    extract_folders = [
        str(path.relative_to(base)).replace("\\", "/")
        for path in (base / "data" / "generated").glob("qbcpl_run019_extract_for_analysis_*")
        if path.is_dir()
    ] if (base / "data" / "generated").exists() else []
    tracked_internal = _tracked_internal_source_findings(tracked_files)
    source_present = bool(zip_info.get("exists")) or any(item.get("exists") for item in residualops_info)
    if tracked_internal:
        decision = "BLOCK_INTERNAL_SOURCE_TRACKED"
    elif source_present:
        decision = "PASS_SOURCE_INPUTS_PROTECTED"
    else:
        decision = "HOLD_SOURCE_INPUTS_MISSING"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "qbcpl_zip": zip_info,
        "residualops_folders": residualops_info,
        "analysis_extract_folders": extract_folders,
        "tracked_internal_source_findings": tracked_internal[:100],
        "source_inputs_commit_allowed": False,
        "public_summary_commit_allowed": True,
        "claim_ceiling": "internal source analysis and productization planning only",
        "must_not_claim": [
            "product readiness",
            "security certification",
            "quality guarantee",
            "legal/safety readiness",
            "external action authorization",
        ],
        "external_actions_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result, root=base)
    return result


def main() -> None:
    result = run_source_intake_audit()
    print(f"roe_source_intake_audit: {result['decision']} commit_allowed={result['source_inputs_commit_allowed']}")


if __name__ == "__main__":
    main()
