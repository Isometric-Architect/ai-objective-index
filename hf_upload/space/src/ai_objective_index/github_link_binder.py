from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OWNER = "Isometric-Architect"
REPO = "ai-objective-index"
REPO_URL = f"https://github.com/{OWNER}/{REPO}"
OUTPUT_PATH = Path("github_upload/GITHUB_LINK_BINDING_RESULT.json")

DEFAULT_FILES = [
    "launch/manual_public_beta_v0_2/FINAL_LINKS_PLACEHOLDER.md",
    "launch/manual_public_beta_v0_2/GITHUB_RELEASE_DRAFT.md",
    "launch/manual_public_beta_v0_2/README_LAUNCH_STEPS.md",
    "release/public_beta_v0_2/README_PUBLIC_BETA_v0_2.md",
    "release/public_beta_v0_2/MANUAL_PUBLISH_CHECKLIST_v0_2.md",
    "docs/community_launch.md",
    "docs/public_beta_release_plan.md",
    "README.md",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def bind_text(text: str, repo_url: str = REPO_URL) -> tuple[str, bool]:
    original = text
    if "GitHub release URL:" in text and "repo staging:" not in text:
        text = text.replace("GitHub release URL:", f"GitHub release URL: TODO after manual release (repo staging: {repo_url})")
    if "GitHub repo:" in text and repo_url not in text:
        text = text.replace("GitHub repo:", f"GitHub repo: {repo_url}")
    if "GitHub:" in text and repo_url not in text:
        text = text.replace("GitHub:", f"GitHub: {repo_url}")
    if "- Hugging Face Space:" in text and "Hugging Face Space: TODO / HOLD" not in text:
        text = text.replace("- Hugging Face Space:", "- Hugging Face Space: TODO / HOLD - not uploaded by Package 8D")
    if "- Hugging Face Dataset:" in text and "Hugging Face Dataset: TODO / HOLD" not in text:
        text = text.replace("- Hugging Face Dataset:", "- Hugging Face Dataset: TODO / HOLD - not uploaded by Package 8D")
    if "- Docs:" in text and "tree/main/docs" not in text:
        text = text.replace("- Docs:", f"- Docs: {repo_url}/tree/main/docs")
    if "- MCP manifest:" in text and "generated_mcp_tools_manifest.json" not in text:
        text = text.replace("- MCP manifest:", f"- MCP manifest: {repo_url}/blob/main/data/generated_mcp_tools_manifest.json")
    if "- API docs:" in text and "api/openapi.json" not in text:
        text = text.replace("- API docs:", f"- API docs: {repo_url}/blob/main/api/openapi.json")

    marker = "GitHub private staging repository"
    if repo_url not in text:
        text += (
            "\n\n## GitHub Private Staging\n\n"
            f"- {marker}: {repo_url}\n"
            "- Current visibility: private staging unless the user manually switches it.\n"
            "- Public visibility is not claimed by Package 8D.\n"
        )
    elif marker.lower() not in text.lower():
        text += (
            "\n\n## GitHub Private Staging\n\n"
            f"- {marker}: {repo_url}\n"
            "- Current visibility: private staging unless the user manually switches it.\n"
            "- Public visibility is not claimed by Package 8D.\n"
        )
    return text, text != original


def bind_github_links(
    files: list[str | Path] | None = None,
    repo_url: str = REPO_URL,
    write_result: bool = True,
) -> dict[str, Any]:
    root = _repo_root()
    updated_files: list[str] = []
    skipped_files: list[str] = []
    for item in files or DEFAULT_FILES:
        path = Path(item)
        if not path.is_absolute():
            path = root / path
        if not path.exists():
            skipped_files.append(str(path))
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        new_text, changed = bind_text(text, repo_url)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            updated_files.append(str(path.relative_to(root)) if root in path.parents else str(path))

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "updated_files": updated_files,
        "skipped_files": skipped_files,
        "repo_url": repo_url,
        "hf_links_left_as_hold": True,
        "public_visibility_claim_added": False,
        "warnings": [
            "Repository links point to private staging until the user manually changes visibility.",
            "Hugging Face links remain TODO/HOLD.",
        ],
        "actual_publish_performed": False,
        "read_only": True,
        "live_network_used": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = bind_github_links()
    print(
        "github_link_binder: "
        f"updated_files={len(result['updated_files'])} "
        f"repo_url={result['repo_url']} "
        "public_visibility_claim_added=False"
    )


if __name__ == "__main__":
    main()
