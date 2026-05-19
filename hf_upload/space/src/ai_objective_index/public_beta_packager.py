from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .release_claim_audit import run_release_claim_audit, save_release_claim_audit
from .release_readiness import run_release_readiness, save_release_readiness


RELEASE_DIR = Path("release/public_beta_v0_1")

CHECKSUM_TARGETS = [
    "README.md",
    "api/openapi.json",
    "data/generated_mcp_tools_manifest.json",
    "data/generated/datascope_qa_results_v0_2.json",
    "data/generated/beta_readiness_report_v0_2.md",
    "data/registry/mcp_registry_public_beta_index_v0_1.json",
    "data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json",
    "data/registry/mcp_registry_beta_report_v0_1.md",
    "data/registry/mcp_registry_report_v0_1.md",
    "reports/mcp_server_objective_index_v0_1.md",
    "reports/ai_tool_pricing_index_v0_1.md",
    "reports/source_trace_quality_report_v0_1.md",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _release_dir() -> Path:
    path = _repo_root() / RELEASE_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checksums() -> dict[str, Any]:
    root = _repo_root()
    records: dict[str, Any] = {}
    for target in CHECKSUM_TARGETS:
        path = root / target
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


def _readme_public_beta() -> str:
    return """# AI Objective Index Public Beta v0.1

AI Objective Index (AOI) is a read-only MCP/API benchmark and objective comparison engine for AI tools, APIs, SaaS products, and MCP servers.

## Current Scope

- AI tools / APIs / SaaS / MCP servers
- Local sample records
- Local generated fixture extraction records
- Integrated sample + generated scope
- Manual curated records
- Official MCP Registry intake records in offline fixture or explicit live mode

## Data Scopes

- `sample`: default sample records
- `generated`: local fixture extraction records, `EXTRACTED_UNVERIFIED`
- `integrated`: sample + generated records
- `curated`: manually curated candidates
- `public_beta`: curated candidates that pass the evidence gate
- `mcp_registry`: local Official MCP Registry intake records
- `public_beta_mcp`: calibrated registry metadata candidates; not verified or security certified; may be empty in fixture mode

## Run Local API

```powershell
python -m ai_objective_index.api
```

## Run MCP Smoke

```powershell
python -m ai_objective_index.mcp_smoke
```

## Run Hugging Face Demo Locally

```powershell
python hf_demo/app.py
```

## Run Eval And Reports

```powershell
python -m ai_objective_index.eval_runner
python -m ai_objective_index.report_generator
```

## Boundary

AOI is read-only. It is not a quality guarantee, official standard, legal advice, financial advice, medical advice, purchasing advice, procurement advice, compliance certification, or safety certification.

AOI does not broadly crawl live sites, scrape arbitrary pages, follow links, call external LLM APIs, buy, book, pay, log in, send email, submit forms, purchase, connect accounts, verify suppliers, or sign contracts. Official MCP Registry live intake, if used, requires explicit `--allow-network`.
"""


def _release_notes() -> str:
    return """# Release Notes v0.1

This public beta release candidate packages AOI's local read-only benchmark surface:

- Core scoring and comparison engine
- Read-only MCP tool functions
- REST API and OpenAPI export
- Golden query evals and reports
- Hugging Face demo draft
- Generated fixture data integration
- Source-governance metadata
- Data scope QA
- MCP `search` / `fetch` compatibility wrappers
- Curated data path and evidence gate
- Official MCP Registry intake pilot with offline fixture mode

No public release, registry submission, Hugging Face publish, or community post is performed by this package.
"""


def _manual_checklist() -> str:
    return """# Manual Publish Checklist

This is a manual publish checklist. The repository does not publish automatically.

- Review README.
- Run `python -m pytest`.
- Run `python -m ai_objective_index.mcp_smoke`.
- Run `python -m ai_objective_index.datascope_qa`.
- Run `python -m ai_objective_index.beta_readiness`.
- Run `python -m ai_objective_index.release_readiness`.
- Run `python -m ai_objective_index.release_claim_audit`.
- Run `python -m ai_objective_index.registry_intake.mcp_registry_export --use-fixture`.
- Run `python -m ai_objective_index.registry_intake.mcp_registry_eval`.
- Run `python -m ai_objective_index.registry_intake.mcp_registry_report_generator`.
- Run `python -m ai_objective_index.registry_intake.registry_beta_dataset_builder`.
- Run `python -m ai_objective_index.registry_intake.registry_quality_audit`.
- Run `python -m ai_objective_index.registry_intake.registry_beta_report_generator`.
- Create GitHub release manually if desired.
- Create Hugging Face Space manually if desired.
- Create Hugging Face Dataset manually if desired.
- Submit MCP Registry entry manually if desired.
- Post community feedback request manually if desired.
- Do not claim official standard status.
- Do not claim universal adoption.
- Do not claim product quality guarantees, legal/security/compliance certification, or purchasing advice.
"""


def _known_limits() -> str:
    return """# Known Limits

- Public beta release candidate only.
- Local data only.
- Sample and generated fixture records are not comprehensive market coverage.
- Generated, curated, and MCP Registry records remain `EXTRACTED_UNVERIFIED`.
- Registry metadata is not supplier verification or security certification.
- `public_beta_mcp` is a registry metadata candidate scope, not verification or security certification, and may be empty in fixture mode.
- Source traces support fields but do not prove completeness, correctness, legal sufficiency, or currentness.
- Objective scores are fit heuristics, not quality guarantees.
- No live crawling, network fetch, external LLM APIs, automatic publishing, registry submission, payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract signing.
"""


def _claim_boundary_summary() -> str:
    return """# Claim Boundary Summary

Allowed claims:

- AOI is a read-only MCP/API benchmark tool.
- AOI is an objective ranking and comparison engine.
- AOI surfaces source traces, missing fields, score components, warnings, and decision receipts.
- AOI supports `sample`, `generated`, `integrated`, `curated`, `public_beta`, `mcp_registry`, and `public_beta_mcp` local data scopes.
- AOI is experimental v0.1/v0.2 software.

Forbidden claims:

- AOI is an official standard.
- All AI will use AOI.
- AOI guarantees product quality.
- AOI provides legal, security, compliance, medical, financial, purchasing, or procurement certification.
- AOI executes payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract signing.

Productization Mode allows implementation and release preparation. Public claims require product evidence.
"""


def _smoke_commands() -> str:
    return """# Smoke Test Commands

```powershell
python -m pytest
python -m ai_objective_index.mcp_smoke
python -m ai_objective_index.datascope_qa
python -m ai_objective_index.beta_readiness
python -m ai_objective_index.release_readiness
python -m ai_objective_index.release_claim_audit
python -m ai_objective_index.public_beta_packager
python -m ai_objective_index.smoke_all
python -m ai_objective_index.registry_intake.mcp_registry_export --use-fixture
python -m ai_objective_index.registry_intake.mcp_registry_eval
python -m ai_objective_index.registry_intake.mcp_registry_report_generator
python -m ai_objective_index.registry_intake.registry_beta_dataset_builder
python -m ai_objective_index.registry_intake.registry_quality_audit
python -m ai_objective_index.registry_intake.registry_beta_report_generator
```

Expected: commands complete locally without network access, no live crawling, and no actual publishing.
"""


def create_public_beta_pack() -> dict[str, Any]:
    release_dir = _release_dir()
    readiness = run_release_readiness()
    readiness_path = save_release_readiness(readiness)
    claim_audit = run_release_claim_audit()
    claim_audit_path = save_release_claim_audit(claim_audit)

    _write(release_dir / "README_PUBLIC_BETA.md", _readme_public_beta())
    _write(release_dir / "RELEASE_NOTES_v0_1.md", _release_notes())
    _write(release_dir / "MANUAL_PUBLISH_CHECKLIST.md", _manual_checklist())
    _write(release_dir / "KNOWN_LIMITS.md", _known_limits())
    _write(release_dir / "CLAIM_BOUNDARY_SUMMARY.md", _claim_boundary_summary())
    _write(release_dir / "SMOKE_TEST_COMMANDS.md", _smoke_commands())
    (release_dir / "release_readiness_result.json").write_text(
        json.dumps(readiness, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (release_dir / "CHECKSUMS.json").write_text(
        json.dumps(_checksums(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (release_dir / "FILE_MANIFEST.json").write_text(
        json.dumps(_file_manifest(release_dir), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "release_dir": str(release_dir),
        "files": sorted(path.name for path in release_dir.iterdir() if path.is_file()),
        "readiness_token": readiness["overall_token"],
        "claim_audit_token": claim_audit["overall_token"],
        "readiness_path": str(readiness_path),
        "claim_audit_path": str(claim_audit_path),
        "actual_publish_performed": False,
    }


def main() -> None:
    result = create_public_beta_pack()
    print(f"Created public beta release pack: {result['release_dir']}")
    print(f"files={len(result['files'])}")
    print(f"readiness={result['readiness_token']} claim_audit={result['claim_audit_token']}")
    print("actual_publish_performed=False")


if __name__ == "__main__":
    main()
