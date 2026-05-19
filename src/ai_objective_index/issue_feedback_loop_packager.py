from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .public_launch_gate import OUTPUT_DIR


PLAN_PATH = OUTPUT_DIR / "ISSUE_FEEDBACK_LOOP_PLAN.md"

ISSUE_LABELS = [
    "failed-query",
    "wrong-field",
    "scoring-dispute",
    "missing-source-trace",
    "docs-confusion",
    "install-failure",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _load_golden_queries(limit: int = 5) -> list[str]:
    path = _repo_root() / "data" / "golden_queries.json"
    if not path.exists():
        return [
            "browser automation MCP server",
            "web search MCP server",
            "document extraction MCP server",
            "vector database MCP server",
            "code execution MCP server",
        ][:limit]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    queries = payload.get("queries", []) if isinstance(payload, dict) else []
    result: list[str] = []
    for item in queries:
        if isinstance(item, dict) and item.get("query"):
            result.append(str(item["query"]))
        if len(result) >= limit:
            break
    return result


def build_issue_feedback_loop_text(golden_queries: list[str] | None = None) -> str:
    queries = golden_queries or _load_golden_queries()
    query_lines = "\n".join(f"{index}. `{query}`" for index, query in enumerate(queries, start=1))
    label_lines = "\n".join(f"- `{label}`" for label in ISSUE_LABELS)
    return f"""# Issue-Based Feedback Loop

AOI can run a no-contact public beta without private reviewers. Feedback is collected through GitHub Issues instead of direct sales calls, personal outreach, or private reviewer coordination.

## Recommended Labels

{label_lines}

## First Golden Queries

{query_lines}

## Response Workflow

1. Issue received.
2. Classify it as failed query, wrong field, scoring dispute, missing source trace, docs confusion, or install failure.
3. Reproduce locally with `python -m ai_objective_index.smoke_all`, the REST API, MCP tools, or the Hugging Face Space.
4. If valid, add the scenario to golden queries or negative controls.
5. Patch scoring, source traces, docs, or data-scope handling.
6. Run claim and no-secrets audits.
7. Release a patch manually if the owner chooses.

## Boundaries

- No direct sales required.
- No private reviewer dependency.
- No automatic posting.
- No claim that `public_beta_mcp` records are verified, security certified, quality guaranteed, or action-ready.
- No payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim, or supplier verification.
"""


def create_issue_feedback_loop_plan() -> dict[str, Any]:
    text = build_issue_feedback_loop_text()
    path = _write(PLAN_PATH, text)
    return {
        "plan_path": str(path),
        "issue_labels": ISSUE_LABELS,
        "golden_queries": _load_golden_queries(),
        "private_reviewer_required": False,
        "direct_sales_required": False,
        "actual_post_performed": False,
    }


def main() -> None:
    result = create_issue_feedback_loop_plan()
    print(
        "issue_feedback_loop_packager: "
        f"plan={result['plan_path']} "
        f"labels={len(result['issue_labels'])} "
        "private_reviewer_required=False"
    )


if __name__ == "__main__":
    main()
