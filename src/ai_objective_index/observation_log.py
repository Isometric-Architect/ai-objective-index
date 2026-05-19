from __future__ import annotations

from pathlib import Path

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .public_ops_baseline import OUTPUT_DIR


OBSERVATION_PATH = OUTPUT_DIR / "OBSERVATION_LOG_72H.md"
ACTIONS_PATH = OUTPUT_DIR / "NEXT_72H_ACTIONS.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def write_observation_log() -> Path:
    text = f"""# 72-Hour Public Observation Log

## Hour 0 Baseline

- GitHub: {GITHUB_URL}
- Hugging Face Space: {HF_SPACE_URL}
- Hugging Face Dataset: {HF_DATASET_URL}
- public_beta_mcp count:
- Claim boundary checked:
- Sample query result:

## Hour 1 Check

- GitHub README:
- HF Space status:
- HF Dataset visibility:
- Sample query result:
- Notes:

## Hour 24 Check

- GitHub stars:
- GitHub issues:
- HF Space status:
- HF Dataset visibility:
- Notes:

## Hour 48 Check

- GitHub stars:
- GitHub issues:
- HF Space status:
- HF Dataset visibility:
- Notes:

## Hour 72 Check

- GitHub stars:
- GitHub issues:
- HF Space status:
- HF Dataset visibility:
- Failed query reports:
- Missing source trace reports:
- Install failure reports:
- Decision after 72h:

## Reminder

No immediate attention does not mean failure. Public beta signal can be quiet, delayed, or qualitative.
"""
    return _write(OBSERVATION_PATH, text)


def write_next_72h_actions() -> Path:
    text = """# Next 72H Actions

- Do not panic if there are no stars or issues.
- Check the Space once or twice.
- Open one sample query: `browser automation MCP server`.
- Watch issue templates for failed queries, wrong fields, missing source traces, and install failures.
- Do not post to communities yet unless Package 8N or an explicit later decision approves it.
- Keep claims conservative: read-only, source-traced, not verified, not security certified, not a quality guarantee, and not purchasing advice.
"""
    return _write(ACTIONS_PATH, text)


def create_observation_assets() -> dict[str, str]:
    return {
        "observation_log_path": str(write_observation_log()),
        "next_72h_actions_path": str(write_next_72h_actions()),
    }


def main() -> None:
    result = create_observation_assets()
    print(f"observation_log: wrote={result['observation_log_path']}")
    print("next_action=Observe public links and issue loop for 72 hours")


if __name__ == "__main__":
    main()
