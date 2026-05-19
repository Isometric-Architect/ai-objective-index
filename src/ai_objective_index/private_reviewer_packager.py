from __future__ import annotations

from pathlib import Path

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .public_launch_gate import OUTPUT_DIR


INVITE_PATH = OUTPUT_DIR / "PRIVATE_REVIEWER_INVITE_DRAFT.md"
ANNOUNCEMENT_PATH = OUTPUT_DIR / "PUBLIC_ANNOUNCEMENT_DRAFTS.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def create_private_reviewer_pack() -> dict[str, object]:
    invite = f"""# Private Reviewer Invite Draft

You are invited to test a private beta of AI Objective Index.

- GitHub private repo: {GITHUB_URL}
- Hugging Face Space, private: {HF_SPACE_URL}
- Hugging Face Dataset, private: {HF_DATASET_URL}

Please try:

1. `browser automation MCP server`
2. `document extraction MCP server`
3. `vector database MCP server`

Please report:

- wrong field
- bad ranking
- missing source trace
- confusing claim boundary

Please do not redistribute if this remains private. The registry metadata candidates are not verified, not security certified, not a quality guarantee, not purchasing advice, and not action-ready.
"""
    announcements = """# Public Announcement Drafts

These are drafts only. Do not post automatically.

## GitHub README Announcement

AI Objective Index is a read-only, source-traced objective ranking and comparison prototype for AI tools, APIs, SaaS products, and MCP servers. It includes Official MCP Registry metadata candidates in `public_beta_mcp`. Please test and break it. The candidates are not verified, not security certified, not a quality guarantee, and not purchasing advice.

## Hugging Face Discussion

I prepared a private Hugging Face demo/dataset for AOI. It is read-only, objective-based, and source-traced. Please test ranking failures, missing traces, and confusing claim boundaries. It does not buy, book, log in, send email, or execute external actions.

## Show HN / Feedback

Show HN: AI Objective Index - read-only source-traced ranking for MCP servers and AI tools

I built AOI to compare MCP servers and AI tools by explicit objectives and source traces. It uses registry metadata candidates, not verified/safe/certified tools. Please test/break it and send evidence-backed issues.

## OpenAI Developer Community

AOI is a read-only MCP/API benchmark for objective-based comparison. It surfaces missing fields and source traces. It is not a quality guarantee, purchasing advice, or action executor.

## MCP Community

AOI includes a `public_beta_mcp` candidate set based on Official MCP Registry metadata. It is source-traced and read-only, but not verified, not security certified, and not action-ready.
"""
    invite_path = _write(INVITE_PATH, invite)
    announcements_path = _write(ANNOUNCEMENT_PATH, announcements)
    return {
        "invite_path": str(invite_path),
        "announcement_drafts_path": str(announcements_path),
        "private_links_included": True,
        "actual_post_performed": False,
    }


def main() -> None:
    result = create_private_reviewer_pack()
    print(
        "private_reviewer_packager: "
        f"invite={result['invite_path']} "
        "actual_post_performed=False"
    )


if __name__ == "__main__":
    main()
