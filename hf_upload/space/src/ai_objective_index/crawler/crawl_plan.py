from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def load_seed_urls(path: str | Path = "data/seeds/seed_urls_ai_tools.csv") -> list[dict[str, str]]:
    resolved = _resolve_path(path)
    with resolved.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_crawl_plan(
    seed_urls: list[str] | list[dict[str, Any]],
    include_pages: list[str] | None = None,
) -> list[dict[str, Any]]:
    include_pages = include_pages or ["home", "pricing", "docs", "terms", "privacy", "github"]
    plan: list[dict[str, Any]] = []

    for index, item in enumerate(seed_urls, start=1):
        if isinstance(item, str):
            row = {"url": item, "category": "seed_example", "expected_page_type": "unknown", "notes": ""}
        else:
            row = dict(item)
        plan.append(
            {
                "plan_id": f"crawl-plan-{index:03d}",
                "url": row.get("url", ""),
                "category": row.get("category", "seed_example"),
                "expected_page_type": row.get("expected_page_type", "unknown"),
                "notes": row.get("notes", ""),
                "planned_pages": include_pages,
                "read_only": True,
                "network_fetch": False,
            }
        )

    return plan


def main() -> None:
    seeds = load_seed_urls()
    plan = build_crawl_plan(seeds)
    print("AI Objective Index crawl plan preview")
    print("Network fetch: disabled")
    print(json.dumps({"count": len(plan), "items": plan[:10]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
