from __future__ import annotations

import json
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .real_pypi_upload_gate import SDIST_PATH, WHEEL_PATH, TOKEN_PATTERNS, _repo_root


OUTPUT_PATH = Path("public_launch") / "wave12_tech_protection" / "PACKAGE_ARTIFACT_EXPOSURE_AUDIT.json"
BLOCK_NAME_FRAGMENTS = [
    ".pypirc",
    ".env",
    "private_kernel/",
    "private_kernels/",
    "private_data/",
    "private_calibration/",
    "private_negative_controls/",
    "private_provider_priors/",
    "source_0513",
    "source_master",
    "internal_source",
    "raw_source_master",
    "site-packages/",
    "venv/",
    ".pytest_cache/",
]
HOLD_NAME_FRAGMENTS = ["public_launch/", "deployment/", "github_upload/", "huggingface_upload/", "dist/"]


def _is_safe_test_token_fixture(name: str, text: str) -> bool:
    normalized = name.replace("\\", "/").lower()
    return "/tests/" in normalized and (
        "redacts_token" in text
        or "REDACTED_TOKEN_LIKE_TEXT" in text
        or "token_redacted" in text
        or "pypi-secret-token-value" in text
    )


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def inspect_artifact_names(names: Iterable[str]) -> dict[str, Any]:
    blocked: list[str] = []
    review: list[str] = []
    safe: list[str] = []
    for raw in names:
        name = raw.replace("\\", "/").lower()
        if any(fragment in name for fragment in BLOCK_NAME_FRAGMENTS):
            blocked.append(raw)
        elif any(fragment in name for fragment in HOLD_NAME_FRAGMENTS):
            review.append(raw)
        else:
            safe.append(raw)
    return {"blocked": blocked, "review": review, "safe_public_artifacts": safe[:100], "entry_count": len(blocked) + len(review) + len(safe)}


def _zip_names(path: Path) -> tuple[list[str], str]:
    try:
        with zipfile.ZipFile(path) as archive:
            return archive.namelist(), ""
    except (OSError, zipfile.BadZipFile, PermissionError) as exc:
        return [], str(exc)


def _tar_names(path: Path) -> tuple[list[str], str]:
    try:
        with tarfile.open(path, "r:gz") as archive:
            return archive.getnames(), ""
    except (OSError, tarfile.TarError, PermissionError) as exc:
        return [], str(exc)


def _artifact_token_findings(path: Path) -> list[str]:
    findings: list[str] = []
    # Only scan metadata/small text files from archives; names are the primary exposure check.
    try:
        if path.suffix == ".whl":
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    if not name.endswith((".py", ".txt", ".md", ".json", ".toml", "METADATA")):
                        continue
                    data = archive.read(name)
                    if len(data) > 500_000:
                        continue
                    text = data.decode("utf-8", errors="ignore")
                    if _is_safe_test_token_fixture(name, text):
                        continue
                    if any(pattern.search(text) for pattern in TOKEN_PATTERNS):
                        findings.append(name)
        elif path.name.endswith(".tar.gz"):
            with tarfile.open(path, "r:gz") as archive:
                for member in archive.getmembers():
                    if not member.isfile() or member.size > 500_000 or not member.name.endswith((".py", ".txt", ".md", ".json", ".toml")):
                        continue
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        continue
                    text = extracted.read().decode("utf-8", errors="ignore")
                    if _is_safe_test_token_fixture(member.name, text):
                        continue
                    if any(pattern.search(text) for pattern in TOKEN_PATTERNS):
                        findings.append(member.name)
    except (OSError, zipfile.BadZipFile, tarfile.TarError, PermissionError):
        return findings
    return findings


def run_package_artifact_exposure_audit(write_result: bool = True) -> dict[str, Any]:
    wheel = _repo_root() / WHEEL_PATH
    sdist = _repo_root() / SDIST_PATH
    artifacts: list[dict[str, Any]] = []
    blocked: list[str] = []
    review: list[str] = []
    warnings: list[str] = []
    token_findings: list[str] = []

    for path, kind in [(wheel, "wheel"), (sdist, "sdist")]:
        if not path.exists():
            warnings.append(f"{kind} missing: {path}")
            artifacts.append({"kind": kind, "path": str(path), "exists": False, "read_error": "missing", "entry_count": 0, "blocked": [], "review": []})
            continue
        names, error = _zip_names(path) if kind == "wheel" else _tar_names(path)
        inspected = inspect_artifact_names(names)
        item_token_findings = _artifact_token_findings(path) if not error else []
        token_findings.extend(f"{kind}:{name}" for name in item_token_findings)
        blocked.extend(f"{kind}:{name}" for name in inspected["blocked"])
        review.extend(f"{kind}:{name}" for name in inspected["review"])
        if error:
            warnings.append(f"{kind} could not be read: {error}")
        artifacts.append({"kind": kind, "path": str(path), "exists": True, "read_error": error, **inspected, "token_findings": item_token_findings})

    if token_findings or blocked:
        decision = "BLOCK_SENSITIVE_ARTIFACT_IN_PACKAGE"
    elif warnings or review:
        decision = "HOLD_PACKAGE_ARTIFACT_REVIEW"
    else:
        decision = "PASS_PACKAGE_ARTIFACT_SAFE"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "artifacts": artifacts,
        "blocked_entries": blocked[:100],
        "review_entries": review[:100],
        "token_findings": token_findings,
        "warnings": warnings,
        "remediation_if_block": "Do not yank automatically. Bump to 0.3.0a2 with corrected package manifest, rebuild, verify, upload, then rerun this audit.",
        "mcp_registry_submission_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_package_artifact_exposure_audit()
    print(f"package_artifact_exposure_audit: {result['decision']}")


if __name__ == "__main__":
    main()
