from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ARCHIVE_DIR = Path("dist/ai_objective_index_public_beta_v0_2")
DEFAULT_MANIFEST_PATH = Path("data/generated/launch_archive_manifest_v0_2.json")

COPY_FILES = [
    "README.md",
    "AGENTS.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "api/openapi.json",
    "data/generated_mcp_tools_manifest.json",
    "data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json",
    "data/registry/mcp_registry_beta_candidates_v0_1.jsonl",
    "data/registry/mcp_registry_beta_report_v0_1.md",
    "docs/public_beta_release_plan.md",
    "docs/manual_publish_checklist.md",
    "docs/public_claim_policy.md",
    "docs/mcp_registry_intake.md",
    "docs/openai_mcp_compatibility.md",
]

COPY_DIRS = [
    "docs",
    "examples",
    "hf_demo",
    "hf_dataset",
    "reports",
    "release/public_beta_v0_2",
    "launch/manual_public_beta_v0_2",
    "schemas",
]

EXCLUDED_DIR_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    "data/source_cache",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_target() -> Path:
    root = _repo_root()
    target = root / ARCHIVE_DIR
    dist = root / "dist"
    resolved = target.resolve()
    if dist.resolve() not in resolved.parents and resolved != dist.resolve():
        raise RuntimeError("Archive target must stay under dist/.")
    return target


def _copy_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _copy_dir(src: Path, dest: Path) -> list[Path]:
    copied: list[Path] = []
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in item.parts):
            continue
        rel = item.relative_to(src)
        target = dest / rel
        _copy_file(item, target)
        copied.append(target)
    return copied


def _write_archive_readme(target: Path) -> None:
    (target / "README.md").write_text(
        """# AI Objective Index Public Beta v0.2 Archive

This local archive contains manual public beta release materials for AOI.

It is read-only and local-data-only. Nothing in this folder publishes, uploads, posts, submits to MCP Registry, buys, books, logs in, sends email, purchases, verifies suppliers, or signs contracts.

`public_beta_mcp` contains Official MCP Registry metadata candidates. They are not verified, not security certified, not quality guaranteed, not purchasing advice, and not action-ready.
""",
        encoding="utf-8",
    )


def build_release_archive(create_zip: bool = True) -> dict[str, Any]:
    root = _repo_root()
    target = _safe_target()
    missing_optional: list[str] = []
    copied_files: list[Path] = []

    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    _write_archive_readme(target)
    copied_files.append(target / "README.md")

    for rel in COPY_FILES:
        src = root / rel
        if src.exists():
            dest = target / rel
            _copy_file(src, dest)
            copied_files.append(dest)
        else:
            missing_optional.append(rel)

    for rel in COPY_DIRS:
        src = root / rel
        if src.exists():
            copied_files.extend(_copy_dir(src, target / rel))
        else:
            missing_optional.append(rel)

    checksum_list = [
        {
            "path": str(path.relative_to(target)).replace("\\", "/"),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in sorted(set(copied_files))
        if path.exists() and path.is_file()
    ]
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "archive_dir": str(target),
        "copied_file_count": len(checksum_list),
        "checksums": checksum_list,
        "missing_optional_files": sorted(set(missing_optional)),
        "actual_publish_performed": False,
        "live_network_used": False,
        "excluded": sorted(EXCLUDED_DIR_NAMES),
    }
    manifest_path = root / DEFAULT_MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    zip_path = root / "dist/ai_objective_index_public_beta_v0_2.zip"
    if create_zip:
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(target.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(root))
        manifest["zip_path"] = str(zip_path)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    result = build_release_archive()
    print(
        "release_archive_builder: "
        f"archive_dir={result['archive_dir']} "
        f"files={result['copied_file_count']} "
        f"missing_optional={len(result['missing_optional_files'])} "
        "actual_publish_performed=False live_network_used=False"
    )


if __name__ == "__main__":
    main()
