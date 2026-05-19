from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .issue_feedback_loop_packager import _load_golden_queries
from .public_launch_gate import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "PUBLIC_ISSUE_LOOP_RESULT.json"
LABELS_PATH = OUTPUT_DIR / "GITHUB_LABELS_SUGGESTED.md"
CHECK_PATH = OUTPUT_DIR / "FIRST_ISSUE_TEMPLATES_CHECK.md"
TEMPLATE_DIR = Path(".github/ISSUE_TEMPLATE")

SUGGESTED_LABELS = [
    "failed-query",
    "wrong-field",
    "scoring-dispute",
    "missing-source-trace",
    "add-tool",
    "install-failure",
    "docs-confusion",
    "good-first-feedback",
    "public-beta",
]

TEMPLATE_TEXTS = {
    "failed_query.md": """---
name: Failed query
about: Report a query that produced weak, missing, or surprising AOI results.
title: "Failed query: "
labels: failed-query, public-beta
---

## Query


## Expected Result


## Actual Result


## Data Scope

- [ ] public_beta_mcp
- [ ] mcp_registry
- [ ] sample
- [ ] other

## Evidence / Source Trace


## Should This Become A Golden Query?

- [ ] Yes
- [ ] No

## Notes

AOI is read-only. `public_beta_mcp` records are not verified, not security certified, and not a quality guarantee.
""",
    "wrong_extracted_field.md": """---
name: Wrong extracted field
about: Report a field that appears wrong or unsupported by its source trace.
title: "Wrong extracted field: "
labels: wrong-field, public-beta
---

## Object ID


## Field


## Current Value


## Expected Value


## Official Source URL Or Registry Evidence


## Notes

AOI does not perform supplier verification or profile modification. Source traces support fields without proving total correctness.
""",
    "scoring_dispute.md": """---
name: Scoring dispute
about: Challenge a ranking or score component.
title: "Scoring dispute: "
labels: scoring-dispute, public-beta
---

## Query


## Object ID


## Current Rank / Score


## Expected Rank / Score


## Score Component

- [ ] relevance
- [ ] capability_fit
- [ ] documentation_quality
- [ ] source_trace_coverage
- [ ] missing_field_penalty
- [ ] other

## Evidence


## Notes

AOI scores are objective-fit signals, not quality guarantees or purchasing advice.
""",
    "add_new_tool.md": """---
name: Add new tool
about: Suggest a new AI tool, API, SaaS product, or MCP server for future indexing.
title: "Add new tool: "
labels: add-tool, public-beta
---

## Tool Name


## Official URL


## Object Type


## Source Trace Candidates


## Why It Belongs


## Notes

AOI does not support supplier claim/verify, paid placement, purchasing, or automatic onboarding.
""",
    "missing_source_trace.md": """---
name: Missing source trace
about: Report a field or result that lacks enough trace evidence.
title: "Missing source trace: "
labels: missing-source-trace, public-beta
---

## Object ID


## Field Or Result


## Missing Evidence


## Suggested Source URL


## Notes

Source trace requests improve transparency. They do not create verification, certification, or action permission.
""",
    "install_failure.md": """---
name: Install failure
about: Report local setup, API, MCP, or Hugging Face demo install trouble.
title: "Install failure: "
labels: install-failure, public-beta
---

## Environment


## Command Run


## Error Output


## Expected Behavior


## Notes

Do not paste secrets, tokens, or private credentials into issues.
""",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def ensure_issue_templates(overwrite: bool = False) -> dict[str, Any]:
    templates_present: list[str] = []
    templates_created: list[str] = []
    root = _repo_root()
    for name, text in TEMPLATE_TEXTS.items():
        path = root / TEMPLATE_DIR / name
        if path.exists() and not overwrite:
            templates_present.append(str(path.relative_to(root)))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        templates_created.append(str(path.relative_to(root)))
    return {"templates_present": templates_present, "templates_created": templates_created}


def write_label_suggestions(labels: list[str] | None = None) -> Path:
    labels = labels or SUGGESTED_LABELS
    label_lines = "\n".join(f"- `{label}`" for label in labels)
    text = f"""# GitHub Labels Suggested

Use these labels for the public beta issue loop:

{label_lines}

These labels are suggestions only. They do not trigger sales outreach, supplier verification, payment, booking, login, email, form submission, purchase, contract signing, or account modification.
"""
    return _write(LABELS_PATH, text)


def write_first_issue_templates_check(golden_queries: list[str] | None = None) -> Path:
    queries = golden_queries or _load_golden_queries(limit=5)
    query_lines = "\n".join(f"{index}. `{query}`" for index, query in enumerate(queries, start=1))
    text = f"""# First Issue Templates Check

## Golden Queries To Try First

{query_lines}

## How To Report A Failure

1. Open a GitHub Issue.
2. Pick the closest template: failed query, wrong field, scoring dispute, missing source trace, add tool, or install failure.
3. Include the query, object ID if known, data scope, expected behavior, actual behavior, and any source trace details.
4. Do not paste API keys, Hugging Face tokens, GitHub tokens, passwords, or private credentials.

## Feedback Model

- No direct sales required.
- No personal reviewer required.
- Issue reports are used to reproduce failures, improve golden queries, patch scoring/source traces/docs, and publish later fixes manually.
- `public_beta_mcp` records are registry metadata candidates, not verified, not security certified, and not a quality guarantee.
"""
    return _write(CHECK_PATH, text)


def run_public_issue_loop(write_result: bool = True) -> dict[str, Any]:
    template_result = ensure_issue_templates()
    labels_path = write_label_suggestions()
    golden_queries = _load_golden_queries(limit=5)
    check_path = write_first_issue_templates_check(golden_queries)
    templates_present = sorted(template_result["templates_present"] + template_result["templates_created"])
    feedback_loop_ready = all(((_repo_root() / TEMPLATE_DIR / name).exists()) for name in TEMPLATE_TEXTS)
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "templates_present": templates_present,
        "templates_created": template_result["templates_created"],
        "labels_suggested": SUGGESTED_LABELS,
        "labels_path": str(labels_path),
        "golden_queries": golden_queries,
        "first_issue_templates_check_path": str(check_path),
        "feedback_loop_ready": feedback_loop_ready,
        "warnings": [
            "GitHub labels are suggestions; create them manually in GitHub if desired.",
            "Issue feedback is not supplier verification, security certification, or quality guarantee.",
        ],
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "read_only": True,
        "live_network_used": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_public_issue_loop()
    print(
        "public_issue_loop: "
        f"ready={result['feedback_loop_ready']} "
        f"templates={len(result['templates_present'])} "
        f"labels={len(result['labels_suggested'])}"
    )


if __name__ == "__main__":
    main()
