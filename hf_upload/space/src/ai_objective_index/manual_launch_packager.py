from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .launch_claim_guard import run_launch_claim_guard, save_launch_claim_guard
from .launch_dry_run import run_launch_dry_run, save_launch_dry_run
from .no_secrets_audit import run_no_secrets_audit, save_no_secrets_audit


LAUNCH_DIR = Path("launch/manual_public_beta_v0_2")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _launch_dir() -> Path:
    path = _repo_root() / LAUNCH_DIR
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


def _counts() -> dict[str, Any]:
    audit = _read_json("data/registry/registry_payload_audit_v0_1.json")
    return {
        "mcp_registry_count": int(audit.get("object_count", 0) or 0),
        "trace_count": int(audit.get("trace_count", 0) or 0),
        "public_beta_mcp_count": int(audit.get("public_beta_mcp_count", 0) or 0),
        "raw_payload_mode": audit.get("raw_payload_mode", "unknown"),
    }


def _readme_launch_steps() -> str:
    return """# Manual Public Beta Launch Steps v0.2

This workspace prepares launch materials only. It does not publish, upload, submit, post, or contact external services.

1. Run `python -m pytest`.
2. Run `python -m ai_objective_index.smoke_all`.
3. Run `python -m ai_objective_index.final_preflight`.
4. Run `python -m ai_objective_index.realdata_claim_audit`.
5. Run `python -m ai_objective_index.manual_launch_packager`.
6. Review `GITHUB_RELEASE_DRAFT.md`.
7. Manually create a GitHub release if desired.
8. Manually create a Hugging Face Space if desired.
9. Manually create a Hugging Face Dataset if desired.
10. Manually post community feedback request if desired.

Keep the release read-only and claim-bounded.
"""


def _github_release_draft(counts: dict[str, Any]) -> str:
    return f"""# GitHub Release Draft: AI Objective Index Public Beta v0.2

AI Objective Index is a read-only MCP/API benchmark and objective comparison engine for AI tools, APIs, SaaS products, and MCP servers.

## Included

- Core scoring and comparison engine
- Read-only MCP tools and `search`/`fetch` compatibility wrappers
- REST API and OpenAPI spec
- Hugging Face demo draft
- Hugging Face dataset draft
- Source-traced Official MCP Registry metadata candidates
- Reports, evals, release pack, and manual launch workspace

## Real Data Scope

- `mcp_registry`: {counts['mcp_registry_count']} registry metadata objects
- `public_beta_mcp`: {counts['public_beta_mcp_count']} registry metadata candidates
- Source traces: {counts['trace_count']}
- Raw payload mode: `{counts['raw_payload_mode']}`

## Run Locally

```powershell
python -m ai_objective_index.api
python -m ai_objective_index.mcp_smoke
python hf_demo/app.py
python -m ai_objective_index.datascope_qa
```

## Boundary

AOI is read-only. It is not a quality guarantee, not security certification, not purchasing advice, and not an official standard.

AOI does not buy, book, pay, log in, send email, submit forms, purchase, connect accounts, verify suppliers, or sign contracts.
"""


def _hf_space_upload_guide() -> str:
    return """# Hugging Face Space Upload Guide

Manual-only steps:

1. Create a Hugging Face Space manually.
2. Choose Gradio for the existing `hf_demo/app.py`.
3. Upload the `hf_demo/` folder and any required project package files manually.
4. Do not put tokens or credentials in the repository.
5. Verify the app launches and `data_scope="public_beta_mcp"` works locally.

The demo is read-only and not a quality guarantee, not security certification, and not purchasing advice.
"""


def _hf_dataset_upload_guide() -> str:
    return """# Hugging Face Dataset Upload Guide

Manual-only steps:

1. Create a Hugging Face Dataset manually.
2. Upload the `hf_dataset/` folder.
3. Include `hf_dataset/README.md` as the dataset card.
4. Verify `mcp_registry_beta_candidates.jsonl` and `mcp_registry_source_traces.jsonl` are present.

Registry metadata candidates are not verified, not security certified, not quality guaranteed, and not action-ready.
"""


def _community_post_drafts() -> str:
    return """# Community Post Drafts

## Show HN / Feedback

AI Objective Index is a read-only MCP/API benchmark for comparing AI tools and MCP servers by explicit objectives, source traces, missing fields, and decision receipts.

It now includes source-traced Official MCP Registry metadata candidates. Please test/break it and file failed queries or missing source trace issues.

The candidates are not verified, not security certified, and not a quality guarantee.

## OpenAI Developer Community

I am testing AOI, a read-only MCP/API objective ranking prototype with source traces and `public_beta_mcp` registry metadata candidates. Please test/break it, especially score explanations and missing-field behavior.

## MCP Community

AOI exposes source-traced Official MCP Registry metadata candidates through read-only MCP/API surfaces. Please test/break the rankings and source trace coverage. This is not verification, security certification, or quality guarantee.

## Hugging Face Discussion

Local demo and dataset drafts are prepared for manual upload. They are read-only and intended for benchmark feedback, not purchasing advice or action execution.

## GitHub README Announcement

Public beta v0.2 release candidate is ready for manual review. It includes read-only MCP/API tools, OpenAPI, HF demo draft, registry metadata candidates, reports, checksums, and claim-boundary docs.
"""


def _mcp_registry_submission_draft() -> str:
    return """# MCP Registry Submission Draft

This is a draft only. It is not submitted automatically.

## Tool Names

- `search`
- `fetch`
- `search_objectives`
- `rank_options`
- `compare_tools`
- `explain_score`
- `get_source_trace`
- `list_missing_fields`
- `generate_decision_receipt`

## Manifest

- `data/generated_mcp_tools_manifest.json`

## Safety Statement

All tools are read-only. No payment, booking, login, email sending, form submission, purchase, account connection, supplier verification, or contract signing tools are exposed.

## Source Trace Availability

AOI provides field-level source traces where local data includes them.

## Limitations

AOI is not a quality guarantee, not security certification, not supplier verification, and not purchasing advice.

## Manual Submission Checklist

- Review manifest.
- Run smoke tests.
- Review final claim boundary.
- Submit manually only if desired.
"""


def _final_safety_checklist() -> str:
    return """# Final Safety Checklist

- No publish performed.
- No live crawling.
- No scraping.
- No link following.
- No payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract signing.
- No supplier verification claim.
- `public_beta_mcp` candidates are not verified.
- Claim audit PASS required.
- No secrets audit PASS or reviewed HOLD required.
"""


def _final_claim_boundary() -> str:
    return """# Final Claim Boundary

Allowed:

- AOI is a read-only MCP/API benchmark and objective comparison engine.
- AOI includes source-traced Official MCP Registry metadata candidates.
- AOI surfaces source traces, missing fields, warnings, scores, and decision receipts.

Forbidden:

- Verified MCP servers.
- Safe MCP servers.
- Security certification.
- Quality guarantee.
- Purchasing advice.
- Official standard.
- Automatic payment, booking, login, email, form submission, purchase, supplier verification, or contract signing.
"""


def _final_known_limits() -> str:
    return """# Final Known Limits

- Registry metadata only.
- Not verified.
- No repository, documentation, or package page fetch.
- No security certification.
- No quality guarantee.
- No action permission.
- No automatic public release.
- No live network is required for launch packaging.
"""


def _final_links_placeholder() -> str:
    return """# Final Links Placeholder

- GitHub release URL:
- Hugging Face Space:
- Hugging Face Dataset:
- Docs:
- MCP manifest:
- API docs:
"""


def _file_manifest(launch_dir: Path) -> dict[str, Any]:
    files = []
    for path in sorted(launch_dir.glob("*")):
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
        "launch_dir": str(LAUNCH_DIR),
        "file_count": len(files),
        "files": files,
        "actual_publish_performed": False,
    }


def _checksums(launch_dir: Path) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "algorithm": "sha256",
        "files": {
            str(path.relative_to(_repo_root())): {
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in sorted(launch_dir.glob("*"))
            if path.is_file()
        },
    }


def create_manual_launch_pack() -> dict[str, Any]:
    launch_dir = _launch_dir()
    counts = _counts()
    _write(launch_dir / "README_LAUNCH_STEPS.md", _readme_launch_steps())
    _write(launch_dir / "GITHUB_RELEASE_DRAFT.md", _github_release_draft(counts))
    _write(launch_dir / "HUGGINGFACE_SPACE_UPLOAD_GUIDE.md", _hf_space_upload_guide())
    _write(launch_dir / "HUGGINGFACE_DATASET_UPLOAD_GUIDE.md", _hf_dataset_upload_guide())
    _write(launch_dir / "COMMUNITY_POST_DRAFTS.md", _community_post_drafts())
    _write(launch_dir / "MCP_REGISTRY_SUBMISSION_DRAFT.md", _mcp_registry_submission_draft())
    _write(launch_dir / "FINAL_SAFETY_CHECKLIST.md", _final_safety_checklist())
    _write(launch_dir / "FINAL_CLAIM_BOUNDARY.md", _final_claim_boundary())
    _write(launch_dir / "FINAL_KNOWN_LIMITS.md", _final_known_limits())
    _write(launch_dir / "FINAL_LINKS_PLACEHOLDER.md", _final_links_placeholder())

    dry_run = run_launch_dry_run()
    dry_run_path = save_launch_dry_run(dry_run)
    no_secrets = run_no_secrets_audit()
    no_secrets_path = save_no_secrets_audit(no_secrets)
    claim_guard = run_launch_claim_guard()
    claim_guard_path = save_launch_claim_guard(claim_guard)

    (launch_dir / "LOCAL_DRY_RUN_RESULT.json").write_text(
        json.dumps(dry_run, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (launch_dir / "NO_SECRETS_AUDIT_RESULT.json").write_text(
        json.dumps(no_secrets, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (launch_dir / "LAUNCH_CLAIM_GUARD_RESULT.json").write_text(
        json.dumps(claim_guard, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (launch_dir / "LAUNCH_FILE_MANIFEST.json").write_text(
        json.dumps(_file_manifest(launch_dir), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (launch_dir / "LAUNCH_CHECKSUMS.json").write_text(
        json.dumps(_checksums(launch_dir), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "launch_dir": str(launch_dir),
        "files": sorted(path.name for path in launch_dir.iterdir() if path.is_file()),
        "dry_run_pass": dry_run["pass"],
        "no_secrets_token": no_secrets["overall_token"],
        "claim_guard_token": claim_guard["overall_token"],
        "dry_run_path": str(dry_run_path),
        "no_secrets_path": str(no_secrets_path),
        "claim_guard_path": str(claim_guard_path),
        "actual_publish_performed": False,
        "live_network_used": False,
    }


def main() -> None:
    result = create_manual_launch_pack()
    print(f"Created manual launch pack: {result['launch_dir']}")
    print(
        "manual_launch_packager: "
        f"files={len(result['files'])} "
        f"dry_run_pass={result['dry_run_pass']} "
        f"no_secrets={result['no_secrets_token']} "
        f"claim_guard={result['claim_guard_token']} "
        "actual_publish_performed=False live_network_used=False"
    )


if __name__ == "__main__":
    main()
