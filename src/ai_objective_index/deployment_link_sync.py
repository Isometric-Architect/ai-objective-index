from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


GITHUB_URL = "https://github.com/Isometric-Architect/ai-objective-index"
HF_SPACE_URL = "https://huggingface.co/spaces/edict-lab/ai-objective-index-demo"
HF_DATASET_URL = "https://huggingface.co/datasets/edict-lab/ai-objective-index-sample"
OUTPUT_DIR = Path("deployment/private_deployment_v0_2")
OUTPUT_PATH = OUTPUT_DIR / "LINK_SYNC_RESULT.json"

DEFAULT_FILES = [
    "README.md",
    "docs/huggingface_demo.md",
    "docs/manual_publish_checklist.md",
    "docs/public_beta_release_plan.md",
    "docs/community_launch.md",
    "launch/manual_public_beta_v0_2/FINAL_LINKS_PLACEHOLDER.md",
    "launch/manual_public_beta_v0_2/README_LAUNCH_STEPS.md",
    "launch/manual_public_beta_v0_2/GITHUB_RELEASE_DRAFT.md",
    "release/public_beta_v0_2/README_PUBLIC_BETA_v0_2.md",
    "hf_upload/space/README.md",
    "hf_upload/dataset/README.md",
    "hf_dataset/README.md",
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


def private_deployment_block(
    github_url: str = GITHUB_URL,
    hf_space_url: str = HF_SPACE_URL,
    hf_dataset_url: str = HF_DATASET_URL,
) -> str:
    return f"""## Private Deployment Links

- GitHub private staging repo: {github_url}
- Hugging Face Space, private: {hf_space_url}
- Hugging Face Dataset, private: {hf_dataset_url}
- MCP Registry submission: HOLD, manual only.

These links are private deployment links unless the owner manually changes visibility. They are not a public release claim. `public_beta_mcp` records are source-traced registry metadata candidates; they are not verified, not safe/certified, not security certified, not a quality guarantee, and not purchasing advice.
"""


def sync_text(
    text: str,
    github_url: str = GITHUB_URL,
    hf_space_url: str = HF_SPACE_URL,
    hf_dataset_url: str = HF_DATASET_URL,
) -> tuple[str, bool]:
    original = text
    replacements = {
        "GitHub release URL:": f"GitHub release URL: TODO after manual release (private repo: {github_url})",
        "GitHub repo:": f"GitHub repo: {github_url}",
        "Hugging Face Space: TODO / HOLD": f"Hugging Face Space, private: {hf_space_url}",
        "Hugging Face Dataset: TODO / HOLD": f"Hugging Face Dataset, private: {hf_dataset_url}",
        "Hugging Face Space:": f"Hugging Face Space, private: {hf_space_url}",
        "Hugging Face Dataset:": f"Hugging Face Dataset, private: {hf_dataset_url}",
    }
    for needle, replacement in replacements.items():
        if needle in text and replacement not in text:
            text = text.replace(needle, replacement)

    if github_url not in text or hf_space_url not in text or hf_dataset_url not in text:
        text = text.rstrip() + "\n\n" + private_deployment_block(github_url, hf_space_url, hf_dataset_url)

    lowered = text.lower()
    if "public release is complete" in lowered:
        text = text.replace("public release is complete", "private deployment is available for review")
        text = text.replace("Public release is complete", "Private deployment is available for review")

    return text, text != original


def write_static_assets() -> list[str]:
    assets = {
        OUTPUT_DIR / "PRIVATE_DEPLOYMENT_SUMMARY.md": f"""# Private Deployment Summary

- GitHub repo: {GITHUB_URL}
- Hugging Face Space, private: {HF_SPACE_URL}
- Hugging Face Dataset, private: {HF_DATASET_URL}
- Visibility: private unless manually changed by the owner.
- Public release performed: false.

The Hugging Face Space and Dataset contain read-only AOI demo/data assets. `public_beta_mcp` is a registry metadata candidate set, not verified MCP servers, not security certification, not a quality guarantee, and not purchasing advice.
""",
        OUTPUT_DIR / "POST_DEPLOYMENT_REVIEW_CHECKLIST.md": f"""# Post Deployment Review Checklist

1. Open the private GitHub repo: {GITHUB_URL}
2. Open the private Hugging Face Space: {HF_SPACE_URL}
3. Test query: `browser automation MCP server`.
4. Open the private Hugging Face Dataset: {HF_DATASET_URL}
5. Confirm README claim boundaries.
6. Confirm there is no verified, safe, certified, or quality-guarantee claim.
7. Confirm no tokens are present.
8. Decide whether to keep private, share with a trusted reviewer, or prepare a later public switch.
""",
        OUTPUT_DIR / "TOKEN_REVOCATION_REMINDER.md": """# Token Revocation Reminder

- Do not paste Hugging Face or GitHub tokens into chat.
- Do not commit tokens.
- Do not store tokens in this repository.
- If no further Hugging Face upload is needed, revoke the temporary token:
  Hugging Face Settings -> Access Tokens -> `aoi-private-upload` -> Delete/Revoke.
- If future Hugging Face updates are planned, keep the token only locally and do not share it.
""",
    }
    written: list[str] = []
    for path, text in assets.items():
        _write(path, text)
        written.append(str(path))
    return written


def sync_deployment_links(
    files: list[str | Path] | None = None,
    github_url: str = GITHUB_URL,
    hf_space_url: str = HF_SPACE_URL,
    hf_dataset_url: str = HF_DATASET_URL,
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
        new_text, changed = sync_text(text, github_url, hf_space_url, hf_dataset_url)
        if changed:
            path.write_text(new_text, encoding="utf-8")
            updated_files.append(str(path.relative_to(root)) if root in path.parents else str(path))

    written_assets = write_static_assets()
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "updated_files": updated_files,
        "skipped_files": skipped_files,
        "static_assets": written_assets,
        "github_url": github_url,
        "hf_space_url": hf_space_url,
        "hf_dataset_url": hf_dataset_url,
        "public_claim_added": False,
        "hf_links_private": True,
        "mcp_registry_submission": "HOLD",
        "warnings": [
            "All deployment URLs are private unless the owner manually changes visibility.",
            "No public release, community post, or MCP Registry submission is claimed.",
        ],
        "actual_publish_performed": False,
        "read_only": True,
        "live_network_used": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = sync_deployment_links()
    print(
        "deployment_link_sync: "
        f"updated_files={len(result['updated_files'])} "
        f"github={result['github_url']} "
        "public_claim_added=False"
    )


if __name__ == "__main__":
    main()
