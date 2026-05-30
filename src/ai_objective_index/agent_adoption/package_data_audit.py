from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from . import VERSION, repo_root, timestamp, write_json
from .agent_claim_boundary import scan_paths


OUTPUT_PATH = Path("public_launch") / "aoi_agent_adoption" / "AOI_AGENT_PACKAGE_DATA_AUDIT_RESULT.json"

SOURCE_ARTIFACTS = [
    Path("agent_discovery") / "CAPABILITY_CARD.json",
    Path("agent_discovery") / "CAPABILITY_CARD.md",
    Path("agent_discovery") / "AGENT_DISCOVER_MODE.md",
    Path("agent_discovery") / "AGENT_PREFLIGHT_MODE.md",
    Path("schemas") / "agent" / "aoi_capability_card.schema.json",
    Path("schemas") / "agent" / "aoi_agent_discover_request.schema.json",
    Path("schemas") / "agent" / "aoi_agent_preflight_request.schema.json",
    Path("examples") / "agent_prompts" / "discover_mcp_candidates.md",
    Path("examples") / "agent_prompts" / "preflight_mcp_candidate.md",
    Path("api") / "vnext" / "examples" / "agent" / "discover_request.json",
    Path("api") / "vnext" / "examples" / "agent" / "discover_response.json",
    Path("api") / "vnext" / "examples" / "agent" / "preflight_request.json",
    Path("api") / "vnext" / "examples" / "agent" / "preflight_response.json",
    Path("api") / "vnext" / "examples" / "agent" / "capability_card_response.json",
    Path("api") / "vnext" / "examples" / "agent" / "adoption_status_response.json",
]

SECRET_PATTERN = re.compile(
    r"\b(sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9_]{12,}|hf_[A-Za-z0-9]{12,}|BEGIN [A-Z ]*PRIVATE\s+KEY|api_key\s*=|password\s*=)",
    re.I,
)


def _wheel_path() -> Path:
    return repo_root() / "dist" / f"ai_objective_index-{VERSION}-py3-none-any.whl"


def _wheel_entries(path: Path) -> list[str]:
    if not path.exists():
        return []
    with zipfile.ZipFile(path) as archive:
        return archive.namelist()


def _artifact_in_wheel(entries: list[str], artifact: Path) -> bool:
    normalized = str(artifact).replace("\\", "/")
    return any(entry.endswith(normalized) for entry in entries)


def _resolve_artifact(root: Path, artifact: Path) -> Path:
    return artifact if artifact.exists() else root / artifact


def _display_wheel_path(root: Path, wheel: Path) -> str:
    if not wheel.exists():
        return str(wheel)
    try:
        return str(wheel.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(wheel).replace("\\", "/")


def _scan_secret_like(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists() or not path.is_file() or path.suffix.lower() not in {".md", ".json", ".txt"}:
            continue
        for index, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if SECRET_PATTERN.search(line):
                findings.append(
                    {
                        "kind": "token_or_secret",
                        "path": str(path),
                        "line": index,
                        "text": line.strip()[:180],
                    }
                )
    return findings


def run_package_data_audit(write_result: bool = True) -> dict[str, Any]:
    root = repo_root()
    missing_source = [
        str(path).replace("\\", "/")
        for path in SOURCE_ARTIFACTS
        if not _resolve_artifact(root, path).exists()
    ]
    wheel = _wheel_path()
    entries = _wheel_entries(wheel)
    missing_wheel = [
        str(path).replace("\\", "/")
        for path in SOURCE_ARTIFACTS
        if entries and not _artifact_in_wheel(entries, path)
    ]
    audited_paths = [_resolve_artifact(root, path) for path in SOURCE_ARTIFACTS if _resolve_artifact(root, path).exists()]
    findings = scan_paths(audited_paths)
    private_findings = [item for item in findings if item["kind"] == "private_kernel_value"]
    secret_like = _scan_secret_like(audited_paths)

    if private_findings:
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
    elif secret_like:
        decision = "BLOCK_SECRET_FINDING"
    elif missing_source or missing_wheel:
        decision = "HOLD_MISSING_AGENT_ARTIFACT"
    elif not wheel.exists():
        decision = "HOLD_PACKAGE_DATA_NOT_BUILT"
    else:
        decision = "PASS_AGENT_PACKAGE_DATA_READY"

    result = {
        "schema": "AOI_AgentPackageDataAudit/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "target_version": VERSION,
        "source_artifact_count": len(SOURCE_ARTIFACTS),
        "missing_source_artifacts": missing_source,
        "wheel_path": _display_wheel_path(root, wheel),
        "wheel_exists": wheel.exists(),
        "wheel_entry_count": len(entries),
        "missing_wheel_artifacts": missing_wheel,
        "agent_discovery_included": bool(entries) and all(_artifact_in_wheel(entries, path) for path in SOURCE_ARTIFACTS if str(path).startswith("agent_discovery")),
        "schemas_agent_included": bool(entries) and all(_artifact_in_wheel(entries, path) for path in SOURCE_ARTIFACTS if str(path).startswith("schemas")),
        "examples_included": bool(entries) and all(_artifact_in_wheel(entries, path) for path in SOURCE_ARTIFACTS if str(path).startswith("examples")),
        "api_examples_included": bool(entries) and all(_artifact_in_wheel(entries, path) for path in SOURCE_ARTIFACTS if str(path).startswith("api")),
        "private_kernel_findings": private_findings,
        "secret_findings": secret_like,
        "documented_if_not_included": [],
        "dist_files_committed": False,
        "pypirc_committed": False,
        "mcp_publisher_binary_committed": False,
        "pypi_upload_performed": False,
        "mcp_registry_publish_performed": False,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_package_data_audit()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"agent_package_data_audit: {result['decision']} wheel={result['wheel_exists']}")


if __name__ == "__main__":
    main()
