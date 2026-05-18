from __future__ import annotations

import fnmatch
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .no_secrets_audit import SECRET_PATTERNS


DEFAULT_OUTPUT_PATH = Path("github_upload/GITHUB_REMOTE_STATUS.json")

GITIGNORE_LINES = [
    "# Python",
    "__pycache__/",
    "*.py[cod]",
    "*.pyo",
    ".pytest_cache/",
    "pytest-cache-files-*/",
    "",
    "# Virtual environments",
    ".venv/",
    "venv/",
    "env/",
    "",
    "# Local environment and credentials",
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "credentials.*",
    "secrets.*",
    "token.*",
    "",
    "# Logs and local editor files",
    "*.log",
    ".DS_Store",
    ".idea/",
    ".vscode/",
    "",
    "# Local caches and transient generated folders",
    "data/source_cache/",
    "data/generated/tmp*/",
    "data/generated/test_*/",
    "",
    "# Local manual raw copy at repository root; canonical processed files live under data/registry/",
    "/mcp_registry_raw_v0_1.json",
    "",
    "# Internal source packs used as research input, not public release payload",
    "/SOURCE_0513_REPACK_FINAL_v1/",
    "",
    "# OS/browser/download scratch",
    "*.tmp",
    "*.bak",
    "Thumbs.db",
]

REQUIRED_RELEASE_ASSETS = [
    "README.md",
    "docs",
    "schemas",
    "src",
    "tests",
    "api/openapi.json",
    "data/generated_mcp_tools_manifest.json",
    "data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json",
    "data/registry/mcp_registry_beta_candidates_v0_1.jsonl",
    "release/public_beta_v0_2",
    "launch/manual_public_beta_v0_2",
]

SHOULD_IGNORE_EXAMPLES = [
    "__pycache__/module.pyc",
    ".pytest_cache/v/cache/nodeids",
    "pytest-cache-files-abc123",
    ".env",
    ".env.local",
    "data/source_cache/source.html",
    "data/generated/tmpabc123/file.txt",
    "data/generated/test_example/file.txt",
    "mcp_registry_raw_v0_1.json",
    "SOURCE_0513_REPACK_FINAL_v1/03_CORE.md",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _normalize(path: str | Path) -> str:
    value = str(path).replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def _patterns() -> list[str]:
    return [line.strip() for line in GITIGNORE_LINES if line.strip() and not line.strip().startswith("#")]


def should_ignore_path(path: str | Path) -> bool:
    value = _normalize(path)
    for pattern in _patterns():
        normalized = pattern.lstrip("/")
        if pattern.endswith("/"):
            prefix = normalized.rstrip("/")
            if value == prefix or value.startswith(prefix + "/"):
                return True
            if fnmatch.fnmatch(value, normalized.rstrip("/") + "*"):
                return True
        if fnmatch.fnmatch(value, normalized):
            return True
    return False


def ensure_gitignore(path: str | Path = ".gitignore") -> Path:
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
    lines = existing.splitlines()
    changed = False
    for line in GITIGNORE_LINES:
        if line and line not in lines:
            lines.append(line)
            changed = True
        elif line == "" and (not lines or lines[-1] != ""):
            lines.append(line)
    if changed or not destination.exists():
        destination.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return destination


def build_manual_upload_commands(
    owner: str = "Isometric-Architect",
    repo: str = "ai-objective-index",
    visibility: str = "private",
) -> str:
    visibility_flag = "--public" if visibility == "public" else "--private"
    return f"""# GitHub Upload Commands

These commands are manual fallback instructions. Do not paste tokens into this file.

```powershell
git init
git branch -M main
git add .
git commit -m "Initial AI Objective Index public beta candidate"
gh auth login
gh repo create {owner}/{repo} {visibility_flag} --source=. --remote=origin --push
```

If the remote repository already exists, do not force push. Verify the remote URL first:

```powershell
git remote -v
git push -u origin main
```
"""


def run_git_release_audit() -> dict[str, Any]:
    root = _repo_root()
    ensure_gitignore()
    required = {path: (root / path).exists() for path in REQUIRED_RELEASE_ASSETS}
    ignored_examples = {path: should_ignore_path(path) for path in SHOULD_IGNORE_EXAMPLES}
    zip_path = root / "dist/ai_objective_index_public_beta_v0_2.zip"
    zip_reasonable = (not zip_path.exists()) or zip_path.stat().st_size < 10 * 1024 * 1024
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "required_release_assets": required,
        "missing_required_assets": [path for path, exists in required.items() if not exists],
        "ignored_examples": ignored_examples,
        "all_ignore_examples_covered": all(ignored_examples.values()),
        "secret_pattern_names": [name for name, _pattern in SECRET_PATTERNS],
        "zip_path": str(zip_path),
        "zip_reasonable": zip_reasonable,
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }


def main() -> None:
    result = run_git_release_audit()
    print(
        "git_release_audit: "
        f"missing={len(result['missing_required_assets'])} "
        f"ignore_examples_ok={result['all_ignore_examples_covered']} "
        f"zip_reasonable={result['zip_reasonable']}"
    )


if __name__ == "__main__":
    main()
