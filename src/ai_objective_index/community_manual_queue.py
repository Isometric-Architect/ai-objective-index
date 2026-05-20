from __future__ import annotations

from pathlib import Path

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .github_release_manager import TAG


WAVE2_DIR = Path("public_launch") / "wave2"
QUEUE_PATH = WAVE2_DIR / "COMMUNITY_MANUAL_POST_QUEUE.md"
CHECKLIST_PATH = WAVE2_DIR / "COMMUNITY_MANUAL_POST_CHECKLIST.md"
SUMMARY_PATH = WAVE2_DIR / "WAVE2_SUMMARY.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _post_body() -> str:
    release_url = f"{GITHUB_URL}/releases/tag/{TAG}"
    return f"""# Community Manual Post Queue

No automatic community post is performed by this package.

## Queue

1. GitHub Release page already exists: {release_url}
2. Hugging Face Space is public: {HF_SPACE_URL}
3. Hugging Face Dataset is public: {HF_DATASET_URL}
4. Optional manual targets:
   - Hugging Face Discussion, if the user has the correct permission
   - OpenAI Developer Community
   - MCP community
   - Hacker News Show HN / Feedback
   - Reddit later
   - Product Hunt much later

## Copy-Paste Draft

Title:

[Feedback] AI Objective Index - read-only MCP/API benchmark for objective-based MCP tool ranking

Body:

I'm testing AI Objective Index, a read-only MCP/API benchmark engine that ranks Official MCP Registry metadata candidates by explicit objectives.

It returns:

- ranked candidates
- source traces
- missing fields
- score components
- decision receipts

Current scope:

AI tools / APIs / SaaS / MCP servers.

Important limits:

- not verified
- not security certified
- not a quality guarantee
- no purchasing advice
- no payment/booking/login/email/purchase/contract actions

Please test with:

1. browser automation MCP server
2. web search MCP server
3. document extraction MCP server
4. vector database MCP server
5. code execution MCP server

Links:

GitHub: {GITHUB_URL}

HF Space: {HF_SPACE_URL}

HF Dataset: {HF_DATASET_URL}

GitHub Release: {release_url}

Ask:

Please open issues for failed queries, wrong fields, scoring disputes, missing source traces, or install failures.
"""


def write_community_manual_queue() -> dict[str, str | bool]:
    queue = _write(QUEUE_PATH, _post_body())
    checklist = """# Community Manual Post Checklist

- Confirm GitHub Release opens.
- Confirm HF Space opens and sample query works.
- Confirm HF Dataset card renders.
- Copy-paste only; do not automate posts.
- Keep wording conservative.
- Do not claim verified, safe, security certified, quality guaranteed, production-ready, or purchasing advice.
- Link to GitHub Issues for feedback.
- Post one venue at a time.
"""
    checklist_path = _write(CHECKLIST_PATH, checklist)
    summary = f"""# Wave 2 Summary

Package 8P prepares AI Objective Index for PyPI packaging, MCP Registry metadata readiness, and conservative manual feedback posts.

## Current State

- GitHub Release: {GITHUB_URL}/releases/tag/{TAG}
- Hugging Face Space: {HF_SPACE_URL}
- Hugging Face Dataset: {HF_DATASET_URL}
- PyPI upload performed: false
- TestPyPI upload performed: false
- MCP Registry submission performed: false
- Automatic community posting performed: false

## Readiness Notes

- `.mcp/server.json` is now a PyPI-based MCP Registry candidate.
- MCP Registry submission remains gated until a real PyPI package exists and registry tooling/authentication pass.
- Community launch remains manual copy-paste only.
- The public claim boundary remains: not verified, not security certified, not a quality guarantee, and no purchasing advice.
"""
    summary_path = _write(SUMMARY_PATH, summary)
    return {
        "queue_path": str(queue),
        "checklist_path": str(checklist_path),
        "summary_path": str(summary_path),
        "external_auto_post": False,
        "manual_post_required": True,
    }


def main() -> None:
    result = write_community_manual_queue()
    print(
        "community_manual_queue: "
        f"queue={result['queue_path']} "
        f"external_auto_post={result['external_auto_post']}"
    )


if __name__ == "__main__":
    main()
