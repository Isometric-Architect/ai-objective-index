from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope


WAVE1_DIR = Path("public_launch") / "wave1"
NOTES_PATH = WAVE1_DIR / "GITHUB_RELEASE_NOTES_v0_2_0_public_beta.md"
RESULT_PATH = WAVE1_DIR / "GITHUB_RELEASE_RESULT.json"
TAG = "v0.2.0-public-beta"
TITLE = "AI Objective Index v0.2.0 Public Beta"
REPO = "Isometric-Architect/ai-objective-index"
MAX_ASSET_BYTES = 25 * 1024 * 1024


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _sanitize(value: Any) -> str:
    text = str(value or "")
    lowered = text.lower()
    for marker in ["gho_", "ghp_", "github_pat_", "hf_", "bearer "]:
        index = lowered.find(marker)
        if index >= 0:
            return text[:index] + "[redacted]"
    return text[:1000]


def _run(command: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "command": command,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": _sanitize(completed.stdout),
            "stderr": _sanitize(completed.stderr),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": _sanitize(exc)}


def _read_json(path: str | Path) -> dict[str, Any]:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _count_source_traces() -> int:
    path = _repo_root() / "data/registry/mcp_registry_source_traces_v0_1.jsonl"
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _gh_available() -> bool:
    return bool(shutil.which("gh"))


def _gh_authenticated(runner: Callable[[list[str], int], dict[str, Any]]) -> bool:
    return bool(runner(["gh", "auth", "status"], 60).get("ok"))


def create_release_notes() -> Path:
    public_beta_count = len(get_store_for_scope("public_beta_mcp").list_objects())
    trace_count = _count_source_traces()
    notes = f"""# {TITLE}

AI Objective Index is a read-only MCP/API benchmark engine for objective-based ranking and comparison of AI tools, APIs, SaaS products, and MCP servers.

## Included In This Public Beta

- Read-only Core Engine, REST API, OpenAPI, MCP tool wrappers, and local MCP stdio entrypoint.
- `public_beta_mcp`: {public_beta_count} Official MCP Registry metadata candidates.
- Source traces: {trace_count}.
- GitHub repository: {GITHUB_URL}
- Hugging Face Space: {HF_SPACE_URL}
- Hugging Face Dataset: {HF_DATASET_URL}

## Try These Golden Queries

1. browser automation MCP server
2. web search MCP server
3. document extraction MCP server
4. vector database MCP server
5. code execution MCP server

## Feedback Wanted

Please open GitHub Issues for:

- failed query
- wrong field
- scoring dispute
- missing source trace
- install failure

## Claim Boundary

The registry records are metadata candidates. They are not verified MCP servers, not safe MCP servers, not security certified, not a quality guarantee, not purchasing advice, and not action-ready.

AOI is read-only. It does not perform payment, booking, login, email sending, form submission, purchase, contract signing, supplier claim/verification, account connection, or profile modification.
"""
    return _write(NOTES_PATH, notes)


def _notes_are_safe(path: Path) -> tuple[bool, list[str]]:
    text = (_repo_root() / path).read_text(encoding="utf-8").lower()
    required = ["not verified", "not security certified", "not a quality guarantee", "not purchasing advice", "read-only"]
    missing = [item for item in required if item not in text]
    return not missing, missing


def _asset_candidate() -> dict[str, Any]:
    path = _repo_root() / "dist/ai_objective_index_public_beta_v0_2.zip"
    if not path.exists():
        return {"path": str(path), "exists": False, "upload_allowed": False, "reason": "asset missing"}
    size = path.stat().st_size
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": size,
        "upload_allowed": size <= MAX_ASSET_BYTES,
        "reason": "size_ok" if size <= MAX_ASSET_BYTES else "asset too large",
    }


def _checks_pass() -> tuple[bool, list[str]]:
    failures: list[str] = []
    no_secrets = _read_json("data/generated/no_secrets_audit_result_v0_2.json")
    launch_claim = _read_json("data/generated/launch_claim_guard_result_v0_2.json")
    message_guard = _read_json("public_launch/PUBLIC_BETA_MESSAGE_GUARD_RESULT.json")
    ops = _read_json("public_ops/PUBLIC_OPS_BASELINE_v0_1.json")
    if no_secrets.get("finding_count", 0) > 0:
        failures.append("no_secrets_audit has real findings")
    if launch_claim.get("overall_token") != "PASS":
        failures.append("launch_claim_guard is not PASS")
    if message_guard and message_guard.get("overall_token") != "PASS":
        failures.append("public_beta_message_guard is not PASS")
    if ops and ops.get("public_beta_mcp_count", 0) <= 0:
        failures.append("public_ops_baseline has no public_beta_mcp candidates")
    return not failures, failures


def run_github_release_manager(
    execute: bool = False,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    notes_path = create_release_notes()
    notes_safe, missing_notes = _notes_are_safe(NOTES_PATH)
    gh_available = _gh_available()
    gh_authenticated = _gh_authenticated(runner) if gh_available else False
    asset = _asset_candidate()
    errors: list[str] = []
    warnings: list[str] = []
    release_existing = False
    release_created = False
    url = ""

    if not notes_safe:
        errors.append(f"Release notes are missing claim boundaries: {', '.join(missing_notes)}")

    if execute:
        checks_ok, check_failures = _checks_pass()
        if not checks_ok:
            errors.extend(check_failures)
        if not gh_available:
            errors.append("GitHub CLI is unavailable.")
        if gh_available and not gh_authenticated:
            errors.append("GitHub CLI is not authenticated.")
        if not errors:
            view = runner(["gh", "release", "view", TAG, "--repo", REPO, "--json", "url"], 60)
            if view.get("ok"):
                release_existing = True
                try:
                    payload = json.loads(view.get("stdout", "") or "{}")
                    url = str(payload.get("url") or "")
                except json.JSONDecodeError:
                    url = f"{GITHUB_URL}/releases/tag/{TAG}"
                warnings.append("Release already exists; not deleting or clobbering it.")
            else:
                create = runner(
                    [
                        "gh",
                        "release",
                        "create",
                        TAG,
                        "--repo",
                        REPO,
                        "--title",
                        TITLE,
                        "--notes-file",
                        str(NOTES_PATH),
                        "--prerelease",
                    ],
                    180,
                )
                if create.get("ok"):
                    release_created = True
                    url = create.get("stdout", "").strip() or f"{GITHUB_URL}/releases/tag/{TAG}"
                else:
                    errors.append(f"GitHub release create failed: {create.get('stderr') or create.get('stdout')}")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "release_created": release_created,
        "release_existing": release_existing,
        "tag": TAG,
        "title": TITLE,
        "url": url or f"{GITHUB_URL}/releases/tag/{TAG}",
        "notes_path": str(NOTES_PATH),
        "asset_candidate": asset,
        "asset_uploaded": False,
        "asset_upload_reason": "skipped_conservative_default",
        "gh_available": gh_available,
        "gh_authenticated": gh_authenticated,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
        "community_post_performed": False,
        "mcp_registry_submission_performed": False,
        "no_clobber": True,
    }
    if write_result:
        _write_json(RESULT_PATH, result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Manage AOI GitHub public beta prerelease.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_github_release_manager(execute=bool(args.execute) and not bool(args.dry_run))
    print(
        "github_release_manager: "
        f"dry_run={result['dry_run']} "
        f"release_created={result['release_created']} "
        f"release_existing={result['release_existing']} "
        f"errors={len(result['errors'])}"
    )
    print(f"url={result['url']}")


if __name__ == "__main__":
    main()
