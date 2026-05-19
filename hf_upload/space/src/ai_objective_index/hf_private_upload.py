from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .hf_auth_check import check_hf_auth
from .hf_upload_audit import run_hf_upload_audit
from .hf_upload_packager import create_hf_upload_bundle


OWNER = "edict-lab"
SPACE_NAME = "ai-objective-index-demo"
DATASET_NAME = "ai-objective-index-sample"
OUTPUT_DIR = Path("huggingface_upload")
OUTPUT_PATH = OUTPUT_DIR / "HF_PRIVATE_UPLOAD_RESULT.json"
COMMANDS_PATH = OUTPUT_DIR / "HF_UPLOAD_COMMANDS.md"
BROWSER_STEPS_PATH = OUTPUT_DIR / "HF_BROWSER_FALLBACK_STEPS.md"

IGNORE_PATTERNS = [
    ".git/*",
    ".pytest_cache/*",
    "__pycache__/*",
    "*.pyc",
    ".env",
    ".env.*",
    "*token*",
    "*secret*",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def write_fallback_docs(owner: str = OWNER, space_name: str = SPACE_NAME, dataset_name: str = DATASET_NAME) -> dict[str, str]:
    commands = f"""# Hugging Face CLI Upload Commands

If CLI authentication is needed, run these locally in PowerShell:

```powershell
python -m pip install huggingface_hub
hf auth login
# or
huggingface-cli login
```

Then run:

```powershell
python -m ai_objective_index.hf_private_upload --execute
```

Do not paste Hugging Face tokens into ChatGPT/Codex chat. Do not save tokens in the repository. Do not commit tokens.
"""
    browser = f"""# Hugging Face Browser Fallback Steps

## Space

1. Go to Hugging Face.
2. Click **New > Space**.
3. Owner: `{owner}`.
4. Name: `{space_name}`.
5. SDK: **Gradio**.
6. Visibility: **Private**.
7. Upload all files from `hf_upload/space`.

## Dataset

1. Click **New > Dataset**.
2. Owner: `{owner}`.
3. Name: `{dataset_name}`.
4. Visibility: **Private**.
5. Upload all files from `hf_upload/dataset`.

No tokens or credentials should be added to the repository.
"""
    return {
        "commands": str(_write(COMMANDS_PATH, commands)),
        "browser_steps": str(_write(BROWSER_STEPS_PATH, browser)),
    }


def _validate_upload_folders() -> dict[str, Any]:
    root = _repo_root()
    required = [
        "hf_upload/space/app.py",
        "hf_upload/space/requirements.txt",
        "hf_upload/dataset/README.md",
        "hf_upload/dataset/public_beta_mcp_dataset.json",
    ]
    missing = [path for path in required if not (root / path).exists()]
    return {"ok": not missing, "missing": missing}


def _api() -> Any:
    from huggingface_hub import HfApi

    return HfApi()


def run_hf_private_upload(
    owner: str = OWNER,
    space_name: str = SPACE_NAME,
    dataset_name: str = DATASET_NAME,
    private: bool = True,
    execute: bool = False,
    api: Any | None = None,
) -> dict[str, Any]:
    root = _repo_root()
    create_hf_upload_bundle()
    audit = run_hf_upload_audit()
    validation = _validate_upload_folders()
    space_repo_id = f"{owner}/{space_name}"
    dataset_repo_id = f"{owner}/{dataset_name}"
    errors: list[str] = []
    warnings: list[str] = []
    fallback_docs = write_fallback_docs(owner, space_name, dataset_name)

    if not validation["ok"]:
        errors.append("Required hf_upload files are missing.")
    if audit.get("overall_token") != "PASS":
        errors.append("hf_upload_audit did not pass.")

    result: dict[str, Any] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "authenticated": False,
        "space_repo_id": space_repo_id,
        "dataset_repo_id": dataset_repo_id,
        "space_created_or_exists": False,
        "dataset_created_or_exists": False,
        "space_upload_performed": False,
        "dataset_upload_performed": False,
        "visibility": "private" if private else "private",
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
        "fallback_docs": fallback_docs,
        "next_action": "",
        "actual_upload_performed": False,
        "live_network_used": False,
        "read_only": True,
    }

    if not execute:
        result["next_action"] = "Dry run complete. Run --execute only after local Hugging Face authentication is ready."
        _write_json(OUTPUT_PATH, result)
        return result

    if errors:
        result["next_action"] = "Fix local upload bundle/audit errors before executing upload."
        _write_json(OUTPUT_PATH, result)
        return result

    api = api or _api()
    auth = check_hf_auth(api=api, write_result=True)
    result["authenticated"] = bool(auth.get("authenticated"))
    if not result["authenticated"]:
        result["warnings"].append("Hugging Face CLI/API is not authenticated; no upload attempted.")
        result["next_action"] = "Run hf auth login or use the browser fallback steps. Do not paste tokens into chat."
        _write_json(OUTPUT_PATH, result)
        return result

    try:
        api.create_repo(
            repo_id=space_repo_id,
            repo_type="space",
            private=True,
            space_sdk="gradio",
            exist_ok=True,
        )
        result["space_created_or_exists"] = True
        api.upload_folder(
            repo_id=space_repo_id,
            repo_type="space",
            folder_path=str(root / "hf_upload" / "space"),
            commit_message="Initial AI Objective Index Space demo",
            ignore_patterns=IGNORE_PATTERNS,
        )
        result["space_upload_performed"] = True

        api.create_repo(
            repo_id=dataset_repo_id,
            repo_type="dataset",
            private=True,
            exist_ok=True,
        )
        result["dataset_created_or_exists"] = True
        api.upload_folder(
            repo_id=dataset_repo_id,
            repo_type="dataset",
            folder_path=str(root / "hf_upload" / "dataset"),
            commit_message="Initial AI Objective Index Dataset bundle",
            ignore_patterns=IGNORE_PATTERNS,
        )
        result["dataset_upload_performed"] = True
        result["actual_upload_performed"] = True
        result["live_network_used"] = True
        result["next_action"] = "Run hf_post_upload_qa and review both private Hugging Face repos."
    except Exception as exc:
        result["errors"].append(str(exc)[:500])
        result["next_action"] = "Review upload error. Do not paste tokens into chat."

    _write_json(OUTPUT_PATH, result)
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Private Hugging Face upload helper for AOI.")
    parser.add_argument("--owner", default=OWNER)
    parser.add_argument("--space-name", default=SPACE_NAME)
    parser.add_argument("--dataset-name", default=DATASET_NAME)
    parser.add_argument("--private", default="true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    execute = bool(args.execute) and not bool(args.dry_run)
    result = run_hf_private_upload(
        owner=args.owner,
        space_name=args.space_name,
        dataset_name=args.dataset_name,
        private=True,
        execute=execute,
    )
    print(
        "hf_private_upload: "
        f"dry_run={result['dry_run']} "
        f"authenticated={result['authenticated']} "
        f"space_upload={result['space_upload_performed']} "
        f"dataset_upload={result['dataset_upload_performed']} "
        "token_printed=False"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
