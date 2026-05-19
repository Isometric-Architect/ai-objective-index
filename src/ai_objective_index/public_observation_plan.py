from __future__ import annotations

from pathlib import Path

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .public_launch_gate import OUTPUT_DIR


OBSERVATION_PLAN_PATH = OUTPUT_DIR / "PUBLIC_OBSERVATION_PLAN_72H.md"
GO_NO_GO_NEXT_PATH = OUTPUT_DIR / "POST_PUBLIC_GO_NO_GO_NEXT.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def write_public_observation_plan() -> Path:
    text = f"""# Public Observation Plan: First 72 Hours

## First 1 Hour

- Open the GitHub README: {GITHUB_URL}
- Open the Hugging Face Space: {HF_SPACE_URL}
- Open the Hugging Face Dataset: {HF_DATASET_URL}
- Run the sample query: `browser automation MCP server`.
- Confirm the result shows source traces or limitations.
- Confirm the public pages still say not verified, not security certified, not a quality guarantee, and read-only.

## First 24 Hours

- Watch GitHub stars, issues, and clone signals if visible.
- Watch Hugging Face likes, downloads, and Space runs if visible.
- Check whether any issue reports include failed queries, wrong fields, missing traces, install failures, or docs confusion.
- Do not overreact to weak early signal.

## First 72 Hours

- Collect failures into GitHub Issues.
- Reproduce issues locally before patching.
- Patch only clear bugs, broken docs, missing source traces, or obviously confusing language.
- Add valid failures to golden queries before changing ranking behavior.
- Do not post communities until the public URLs, issue loop, and claim wording are stable.

## What Counts As Signal

- GitHub star, issue, clone/download, Hugging Face Space run, Hugging Face Dataset download, failed query report, missing source trace report, or install failure.

## What Does Not Count

- No immediate attention does not mean failure.
- A high rank is not a quality guarantee.
- A registry metadata candidate is not verification, security certification, or action permission.
"""
    return _write(OBSERVATION_PLAN_PATH, text)


def write_post_public_go_no_go_next() -> Path:
    text = """# Post-Public GO / NO-GO Next

## Option A: Wait And Observe 72 Hours

Recommended default. Watch issues, public links, and basic usage signals before posting broadly.

## Option B: Create GitHub Release

Only after the public pages and issue loop are stable. Keep release wording conservative.

## Option C: Prepare Community Feedback Post

Package 8M should handle any community launch draft or post. Do not post yet.

## Option D: Submit MCP Registry Later

Manual-only. Do not submit until docs, manifest, and public feedback loop are stable.

## Option E: Improve Space UI

Patch the Hugging Face demo if users report confusion, failed queries, or missing source trace visibility.
"""
    return _write(GO_NO_GO_NEXT_PATH, text)


def write_community_post_still_hold() -> Path:
    text = """# Community Post Still HOLD

- Do not post yet.
- Public visibility was just switched.
- First verify public URLs and the GitHub issue loop.
- Community launch should be Package 8M.
- Any later post must say AOI is read-only, source-traced, not verified, not security certified, not a quality guarantee, and not purchasing advice.
"""
    return _write(OUTPUT_DIR / "COMMUNITY_POST_STILL_HOLD.md", text)


def create_public_observation_assets() -> dict[str, str]:
    plan = write_public_observation_plan()
    next_decision = write_post_public_go_no_go_next()
    hold = write_community_post_still_hold()
    return {
        "observation_plan_path": str(plan),
        "post_public_go_no_go_next_path": str(next_decision),
        "community_post_hold_path": str(hold),
    }


def main() -> None:
    result = create_public_observation_assets()
    print(f"public_observation_plan: wrote={result['observation_plan_path']}")
    print("recommended_next_decision=Wait and observe 72 hours before community posting")


if __name__ == "__main__":
    main()
