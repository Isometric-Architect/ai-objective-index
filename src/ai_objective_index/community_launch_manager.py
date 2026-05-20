from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .hf_auth_check import check_hf_auth


WAVE1_DIR = Path("public_launch") / "wave1"
COMMUNITY_DRAFT_PATH = WAVE1_DIR / "COMMUNITY_FEEDBACK_POST_DRAFTS.md"
HF_DRAFT_PATH = WAVE1_DIR / "HUGGINGFACE_DISCUSSION_DRAFT.md"
GH_DRAFT_PATH = WAVE1_DIR / "GITHUB_DISCUSSION_DRAFT.md"
COMMUNITY_RESULT_PATH = WAVE1_DIR / "COMMUNITY_FEEDBACK_POST_RESULT.json"
HF_RESULT_PATH = WAVE1_DIR / "HUGGINGFACE_DISCUSSION_RESULT.json"
GH_RESULT_PATH = WAVE1_DIR / "GITHUB_DISCUSSION_RESULT.json"

TITLE = "[Feedback] AI Objective Index - read-only MCP/API benchmark for objective-based MCP tool ranking"
GOLDEN_QUERIES = [
    "browser automation MCP server",
    "web search MCP server",
    "document extraction MCP server",
    "vector database MCP server",
    "code execution MCP server",
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


def _draft_body() -> str:
    queries = "\n".join(f"{index}. {query}" for index, query in enumerate(GOLDEN_QUERIES, 1))
    return f"""# {TITLE}

I built AI Objective Index, a read-only MCP/API benchmark tool.

It ranks Official MCP Registry metadata candidates by explicit objectives and returns source traces, missing fields, score components, and decision receipts.

Links:

- GitHub: {GITHUB_URL}
- Hugging Face Space: {HF_SPACE_URL}
- Hugging Face Dataset: {HF_DATASET_URL}

Please test with these golden queries:

{queries}

Feedback that would help:

- failed query
- wrong field
- scoring dispute
- missing source trace
- install failure

Claim boundary: the candidates are not verified, not security certified, not a quality guarantee, not purchasing advice, and not action-ready. AOI is read-only and does not buy, book, pay, log in, send email, submit forms, purchase, sign contracts, connect accounts, or verify suppliers.
"""


def create_community_drafts() -> dict[str, str]:
    body = _draft_body()
    community = body + """
## Manual Copy-Paste Targets

- Hacker News / Show HN or Feedback: manual only.
- Reddit: manual only.
- OpenAI Developer Community: manual only.
- MCP community: manual only.

No automatic post is performed for these external platforms.
"""
    hf = body + "\nSuggested Hugging Face discussion target: Space or Dataset discussion.\n"
    gh = body + "\nSuggested GitHub discussion category: General or Announcements, if enabled.\n"
    return {
        "community": str(_write(COMMUNITY_DRAFT_PATH, community)),
        "huggingface": str(_write(HF_DRAFT_PATH, hf)),
        "github": str(_write(GH_DRAFT_PATH, gh)),
    }


def _api() -> Any:
    from huggingface_hub import HfApi

    return HfApi()


def _try_hf_discussion(api: Any, title: str, body: str) -> dict[str, Any]:
    if not hasattr(api, "create_discussion"):
        return {"created": False, "warning": "huggingface_hub create_discussion is unavailable in this environment."}
    try:
        created = api.create_discussion(
            repo_id="edict-lab/ai-objective-index-demo",
            repo_type="space",
            title=title,
            description=body,
        )
        return {"created": True, "url": str(getattr(created, "url", "") or created)}
    except Exception as exc:
        return {"created": False, "warning": str(exc)[:500]}


def run_community_launch_manager(
    execute_safe: bool = False,
    api: Any | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    drafts = create_community_drafts()
    body = _draft_body()
    hf_discussion_created = False
    hf_warnings: list[str] = []
    hf_url = ""

    if execute_safe:
        try:
            api = api or _api()
            auth = check_hf_auth(api=api, write_result=False)
            if auth.get("authenticated"):
                hf_result = _try_hf_discussion(api, TITLE, body)
                hf_discussion_created = bool(hf_result.get("created"))
                hf_url = str(hf_result.get("url") or "")
                if hf_result.get("warning"):
                    hf_warnings.append(str(hf_result["warning"]))
            else:
                hf_warnings.append("Hugging Face API is not authenticated; no HF discussion created.")
        except Exception as exc:
            hf_warnings.append(f"Hugging Face discussion check failed: {str(exc)[:500]}")

    community_result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute_safe,
        "execute_safe": execute_safe,
        "drafts": drafts,
        "hf_discussion_created": hf_discussion_created,
        "github_discussion_created": False,
        "external_manual_posts_created": False,
        "manual_post_required": True,
        "token_printed": False,
        "errors": [],
        "warnings": hf_warnings + [
            "HN, Reddit, OpenAI Developer Community, Product Hunt, and MCP community posts are manual copy-paste only."
        ],
        "community_post_performed": hf_discussion_created,
    }
    hf_result_payload = {
        "generated_at": community_result["generated_at"],
        "dry_run": not execute_safe,
        "execute_safe": execute_safe,
        "hf_discussion_created": hf_discussion_created,
        "url": hf_url,
        "token_printed": False,
        "warnings": hf_warnings,
    }
    github_result_payload = {
        "generated_at": community_result["generated_at"],
        "dry_run": not execute_safe,
        "execute_safe": execute_safe,
        "github_discussion_created": False,
        "manual_post_required": True,
        "token_printed": False,
        "warnings": ["GitHub Discussion auto-post is not implemented; use the draft manually if Discussions are enabled."],
    }
    if write_result:
        _write_json(COMMUNITY_RESULT_PATH, community_result)
        _write_json(HF_RESULT_PATH, hf_result_payload)
        _write_json(GH_RESULT_PATH, github_result_payload)
    return community_result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create conservative community feedback launch drafts.")
    parser.add_argument("--execute-safe", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_community_launch_manager(execute_safe=bool(args.execute_safe) and not bool(args.dry_run))
    print(
        "community_launch_manager: "
        f"dry_run={result['dry_run']} "
        f"hf_discussion_created={result['hf_discussion_created']} "
        f"github_discussion_created={result['github_discussion_created']} "
        f"manual_post_required={result['manual_post_required']}"
    )


if __name__ == "__main__":
    main()
