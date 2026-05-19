from __future__ import annotations

import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .final_preflight import run_final_preflight, save_final_preflight
from .realdata_claim_audit import run_realdata_claim_audit, save_realdata_claim_audit
from .release_candidate_matrix import build_release_candidate_matrix, save_release_candidate_matrix


RELEASE_DIR = Path("release/public_beta_v0_2")

CHECKSUM_TARGETS = [
    "README.md",
    "api/openapi.json",
    "data/generated_mcp_tools_manifest.json",
    "data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json",
    "data/registry/mcp_registry_beta_candidates_v0_1.jsonl",
    "data/generated/final_preflight_result_v0_2.json",
    "data/generated/realdata_claim_audit_v0_2.json",
    "data/generated/release_candidate_matrix_v0_2.json",
    "data/registry/mcp_registry_beta_report_v0_1.md",
    "reports/mcp_server_objective_index_v0_2.md",
    "reports/source_trace_quality_report_v0_2.md",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _release_dir() -> Path:
    path = _repo_root() / RELEASE_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _read_json(path: str | Path) -> dict[str, Any]:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return {}
    try:
        value = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _registry_counts() -> dict[str, Any]:
    audit = _read_json("data/registry/registry_payload_audit_v0_1.json")
    dataset = _read_json("data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json")
    return {
        "raw_payload_mode": audit.get("raw_payload_mode", "unknown"),
        "object_count": int(audit.get("object_count") or dataset.get("object_count") or 0),
        "trace_count": int(audit.get("trace_count") or dataset.get("trace_count") or 0),
        "beta_candidate_count": int(audit.get("public_beta_mcp_count") or dataset.get("beta_candidate_count") or 0),
        "fixture_leak_detected": bool(audit.get("fixture_leak_detected", False)),
        "real_payload_available": bool(audit.get("real_payload_available", False)),
        "live_network_used": bool(audit.get("live_network_used", False)),
    }


def _checksums() -> dict[str, Any]:
    records: dict[str, Any] = {}
    for target in CHECKSUM_TARGETS:
        path = _repo_root() / target
        if path.exists():
            records[target] = {
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
                "status": "present",
            }
        else:
            records[target] = {"status": "missing", "sha256": None, "bytes": 0}
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "algorithm": "sha256",
        "files": records,
    }


def _file_manifest(release_dir: Path) -> dict[str, Any]:
    files = []
    for path in sorted(release_dir.glob("*")):
        if path.is_file():
            files.append(
                {
                    "path": str(path.relative_to(_repo_root())),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "release_dir": str(RELEASE_DIR),
        "file_count": len(files),
        "files": files,
        "actual_publish_performed": False,
    }


def _readme_public_beta(counts: dict[str, Any]) -> str:
    return f"""# AI Objective Index Public Beta v0.2

AI Objective Index (AOI) is a read-only MCP/API benchmark and objective comparison engine for AI tools, APIs, SaaS products, and MCP servers.

## Current Public Beta Data Source

The public beta MCP data source is Official MCP Registry metadata obtained as raw JSON and processed locally.

- Raw payload mode: `{counts['raw_payload_mode']}`
- MCP registry objects: `{counts['object_count']}`
- Source traces: `{counts['trace_count']}`
- `public_beta_mcp` candidates: `{counts['beta_candidate_count']}`
- Fixture leak detected: `{str(counts['fixture_leak_detected']).lower()}`

## Run Locally

```powershell
python -m ai_objective_index.api
python -m ai_objective_index.mcp_smoke
python hf_demo/app.py
python -m ai_objective_index.datascope_qa
```

## Data Scopes

- `sample`: original sample records
- `generated`: local fixture extraction records
- `integrated`: sample + generated records
- `curated`: manually curated candidates
- `public_beta`: curated public beta candidates
- `mcp_registry`: all local Official MCP Registry metadata records
- `public_beta_mcp`: registry metadata candidates, not verified

## Boundary

AOI is read-only. `public_beta_mcp` candidates are not verified MCP servers, not security certified, not quality guaranteed, not purchasing advice, and not action-ready.

AOI does not buy, book, pay, log in, send email, submit forms, purchase, connect accounts, verify suppliers, or sign contracts. Publishing to GitHub, Hugging Face, MCP Registry, or communities is manual and not performed by this packager.
"""


def _release_notes(counts: dict[str, Any]) -> str:
    return f"""# Release Notes v0.2

This release candidate refreshes AOI's public beta package with real/manual Official MCP Registry metadata.

- `mcp_registry` objects: `{counts['object_count']}`
- `public_beta_mcp` candidates: `{counts['beta_candidate_count']}`
- Source traces: `{counts['trace_count']}`
- Raw payload mode: `{counts['raw_payload_mode']}`

All registry objects remain `EXTRACTED_UNVERIFIED` or registry metadata candidates. This is not supplier verification, security certification, quality guarantee, purchasing advice, or action permission.
"""


def _manual_checklist() -> str:
    return """# Manual Publish Checklist v0.2

Run locally before any manual public beta release:

- `python -m pytest`
- `python -m ai_objective_index.datascope_qa`
- `python -m ai_objective_index.beta_readiness`
- `python -m ai_objective_index.registry_intake.registry_payload_audit`
- `python -m ai_objective_index.realdata_claim_audit`
- `python -m ai_objective_index.release_candidate_matrix`
- `python -m ai_objective_index.final_preflight`
- `python -m ai_objective_index.public_beta_realdata_packager`
- `python -m ai_objective_index.smoke_all`

Manual steps only:

- Publish a GitHub release manually if desired.
- Publish a Hugging Face Space or Dataset manually if desired.
- Post community feedback request manually if desired.
- Do not claim verified MCP servers, safe MCP servers, security certification, quality guarantee, purchasing advice, official standard status, or universal adoption.
"""


def _known_limits() -> str:
    return """# Known Limits v0.2

- `public_beta_mcp` is based on Official MCP Registry metadata candidates.
- Candidates are not supplier verified.
- Candidates are not security certified.
- Candidates are not quality guaranteed.
- Candidates are not action-ready.
- AOI source traces support specific fields but do not prove completeness, currentness, safety, legality, or fitness.
- AOI does not crawl, scrape, follow links, fetch repositories/docs/package pages, call external LLM APIs, publish, submit to registries, buy, book, log in, send email, purchase, or sign contracts.
"""


def _claim_boundary_summary() -> str:
    return """# Claim Boundary Summary v0.2

Allowed:

- AOI is a read-only MCP/API benchmark and objective comparison tool.
- AOI can expose Official MCP Registry metadata candidates through `mcp_registry` and `public_beta_mcp`.
- AOI surfaces source traces, missing fields, warnings, decision receipts, and claim boundaries.

Forbidden:

- AOI verifies MCP servers.
- AOI certifies MCP server security or safety.
- AOI guarantees quality.
- AOI provides purchasing, legal, financial, medical, compliance, or procurement advice.
- AOI executes payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract signing.
"""


def _real_data_summary(counts: dict[str, Any]) -> str:
    return f"""# Real Data Summary v0.2

- Source of data: Official MCP Registry API raw JSON, manually/live obtained and processed locally.
- Raw payload mode: `{counts['raw_payload_mode']}`
- Object count: `{counts['object_count']}`
- Source trace count: `{counts['trace_count']}`
- Beta candidate count: `{counts['beta_candidate_count']}`
- Fixture leak detected: `{str(counts['fixture_leak_detected']).lower()}`
- Live network used in final processing: `false`
- Real payload available: `{str(counts['real_payload_available']).lower()}`

The data is not supplier verification, security certification, quality guarantee, purchasing advice, or action permission.
"""


def _smoke_commands() -> str:
    return """# Smoke Test Commands v0.2

```powershell
python -m pytest
python -m ai_objective_index.realdata_claim_audit
python -m ai_objective_index.release_candidate_matrix
python -m ai_objective_index.final_preflight
python -m ai_objective_index.public_beta_realdata_packager
python -m ai_objective_index.smoke_all
```

Expected: commands complete locally, no network is required, no publish occurs, and no forbidden actions are exposed.
"""


def _update_hf_dataset(counts: dict[str, Any]) -> None:
    dataset_dir = _repo_root() / "hf_dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    source_candidates = _repo_root() / "data/registry/mcp_registry_beta_candidates_v0_1.jsonl"
    source_traces = _repo_root() / "data/registry/mcp_registry_source_traces_v0_1.jsonl"
    if source_candidates.exists():
        shutil.copyfile(source_candidates, dataset_dir / "mcp_registry_beta_candidates.jsonl")
    if source_traces.exists():
        shutil.copyfile(source_traces, dataset_dir / "mcp_registry_source_traces.jsonl")
    _write(
        dataset_dir / "README.md",
        f"""# Dataset Card: ai-objective-index-sample

## Dataset Name

`ai-objective-index-sample`

## Scope

This local dataset draft contains AOI sample/extracted benchmark records and, when available, `public_beta_mcp` Official MCP Registry metadata candidates.

## Real Registry Candidate Files

- `mcp_registry_beta_candidates.jsonl`: `public_beta_mcp` registry metadata candidates.
- `mcp_registry_source_traces.jsonl`: source traces derived from registry metadata.

Current local counts:

- MCP registry objects: `{counts['object_count']}`
- Source traces: `{counts['trace_count']}`
- `public_beta_mcp` candidates: `{counts['beta_candidate_count']}`

## Source Trace Explanation

`SourceTrace` links a field to a source URL, title, snippet, retrieval timestamp, and confidence value. A trace supports a field, but it does not prove completeness, currentness, legality, safety, or quality.

## Intended Use

Benchmarking and testing objective ranking for AI tools/APIs/SaaS/MCP servers.

## Not Intended For

This dataset is not intended for automated purchase, legal decisions, financial decisions, medical decisions, safety certification, security certification, or quality guarantees.

## Limitations

Registry candidates are not verified, not security certified, not quality guaranteed, and not purchasing advice. This dataset is not a quality guarantee. This repository does not automatically publish to Hugging Face.
""",
    )


def _write_reports(counts: dict[str, Any]) -> None:
    reports_dir = _repo_root() / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    _write(
        reports_dir / "mcp_server_objective_index_v0_2.md",
        f"""# MCP Server Objective Index v0.2

Generated at: `{datetime.now(UTC).isoformat()}`

This report is based on Official MCP Registry metadata candidates processed locally.

- MCP registry objects: `{counts['object_count']}`
- `public_beta_mcp` candidates: `{counts['beta_candidate_count']}`
- Source traces: `{counts['trace_count']}`
- Raw payload mode: `{counts['raw_payload_mode']}`

This report is not a security certification, supplier verification, quality guarantee, purchasing advice, or action permission.
""",
    )
    _write(
        reports_dir / "source_trace_quality_report_v0_2.md",
        f"""# Source Trace Quality Report v0.2

Generated at: `{datetime.now(UTC).isoformat()}`

This report summarizes source-trace coverage for the locally processed Official MCP Registry metadata candidates.

- Source traces: `{counts['trace_count']}`
- Candidate count: `{counts['beta_candidate_count']}`
- Fixture leak detected: `{str(counts['fixture_leak_detected']).lower()}`

Source traces support specific fields but do not prove completeness, currentness, safety, legality, security certification, supplier verification, or quality.
""",
    )


def create_public_beta_realdata_pack() -> dict[str, Any]:
    release_dir = _release_dir()
    counts = _registry_counts()

    _update_hf_dataset(counts)
    _write_reports(counts)

    _write(release_dir / "README_PUBLIC_BETA_v0_2.md", _readme_public_beta(counts))
    _write(release_dir / "RELEASE_NOTES_v0_2.md", _release_notes(counts))
    _write(release_dir / "MANUAL_PUBLISH_CHECKLIST_v0_2.md", _manual_checklist())
    _write(release_dir / "KNOWN_LIMITS_v0_2.md", _known_limits())
    _write(release_dir / "CLAIM_BOUNDARY_SUMMARY_v0_2.md", _claim_boundary_summary())
    _write(release_dir / "REAL_DATA_SUMMARY_v0_2.md", _real_data_summary(counts))
    _write(release_dir / "SMOKE_TEST_COMMANDS_v0_2.md", _smoke_commands())

    claim_audit = run_realdata_claim_audit()
    claim_audit_path = save_realdata_claim_audit(claim_audit)
    matrix = build_release_candidate_matrix()
    matrix_path = save_release_candidate_matrix(matrix)
    preflight = run_final_preflight()
    preflight_path = save_final_preflight(preflight)

    (release_dir / "final_preflight_result_v0_2.json").write_text(
        json.dumps(preflight, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (release_dir / "CHECKSUMS_v0_2.json").write_text(
        json.dumps(_checksums(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (release_dir / "FILE_MANIFEST_v0_2.json").write_text(
        json.dumps(_file_manifest(release_dir), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "release_dir": str(release_dir),
        "files": sorted(path.name for path in release_dir.iterdir() if path.is_file()),
        "final_preflight_token": preflight["overall_token"],
        "claim_audit_token": claim_audit["overall_token"],
        "matrix_token": matrix["overall_token"],
        "public_beta_mcp_count": counts["beta_candidate_count"],
        "claim_audit_path": str(claim_audit_path),
        "matrix_path": str(matrix_path),
        "preflight_path": str(preflight_path),
        "actual_publish_performed": False,
        "live_network_used": False,
    }


def main() -> None:
    result = create_public_beta_realdata_pack()
    print(f"Created public beta v0.2 release pack: {result['release_dir']}")
    print(
        "public_beta_realdata_packager: "
        f"files={len(result['files'])} "
        f"final_preflight={result['final_preflight_token']} "
        f"claim_audit={result['claim_audit_token']} "
        f"public_beta_mcp={result['public_beta_mcp_count']} "
        "actual_publish_performed=False live_network_used=False"
    )


if __name__ == "__main__":
    main()
