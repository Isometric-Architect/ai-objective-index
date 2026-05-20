from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .public_metrics_snapshot import OBSERVATION_DIR, run_public_metrics_snapshot


VALID_PHASES = {"0h", "24h", "48h", "72h"}
ACTIVE_LOG_PATH = OBSERVATION_DIR / "OBSERVATION_LOG_72H_ACTIVE.md"
TEMPLATE_PATHS = {
    "24h": OBSERVATION_DIR / "OBSERVATION_SNAPSHOT_24H.template.json",
    "48h": OBSERVATION_DIR / "OBSERVATION_SNAPSHOT_48H.template.json",
    "72h": OBSERVATION_DIR / "OBSERVATION_SNAPSHOT_72H.template.json",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _append(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(text)
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _template_payload(phase: str) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "phase": phase,
        "status": "template",
        "github_stars": "fill_manually_or_run_snapshot",
        "github_open_issues": "fill_manually_or_run_snapshot",
        "hf_space_status": "fill_manually_or_run_snapshot",
        "hf_dataset_visibility": "fill_manually_or_run_snapshot",
        "sample_query_result": "not_checked",
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "notes": [],
    }


def create_phase_templates() -> list[str]:
    written: list[str] = []
    for phase, path in TEMPLATE_PATHS.items():
        _write_json(path, _template_payload(phase))
        written.append(str(path))
    return written


def _ensure_active_log() -> None:
    full = _repo_root() / ACTIVE_LOG_PATH
    if full.exists():
        return
    _write(
        ACTIVE_LOG_PATH,
        "# Active 72-Hour Public Observation Log\n\n"
        "This log tracks public visibility health without posting to communities, creating a GitHub Release, or submitting to MCP Registry.\n\n",
    )


def _append_phase_log(phase: str, summary: dict[str, Any]) -> None:
    _ensure_active_log()
    lines = [
        f"## Phase {phase} - {datetime.now(UTC).isoformat()}",
        "",
        f"- public_beta_mcp count: `{summary.get('public_beta_mcp_count', 'not_checked')}`",
        f"- GitHub stars: `{summary.get('github_stars', 'not_checked')}`",
        f"- GitHub open issues: `{summary.get('github_open_issues', 'not_checked')}`",
        f"- HF Space status: `{summary.get('hf_space_status', 'not_checked')}`",
        "- Community post performed: `false`",
        "- GitHub Release created: `false`",
        "- MCP Registry submission performed: `false`",
        "",
    ]
    _append(ACTIVE_LOG_PATH, "\n".join(lines))


def run_public_observation_phase(phase: str = "0h", write_result: bool = True) -> dict[str, Any]:
    if phase not in VALID_PHASES:
        raise ValueError(f"Unsupported observation phase: {phase}")

    create_phase_templates()
    if phase == "0h":
        snapshot = run_public_metrics_snapshot(write_result=write_result)
        summary = {
            "phase": phase,
            "output_path": "public_ops/observation/OBSERVATION_SNAPSHOT_0H.json",
            "public_beta_mcp_count": snapshot["public_beta_mcp_count"],
            "github_stars": snapshot["github"]["stars_count"],
            "github_open_issues": snapshot["github"]["open_issues_count"],
            "hf_space_status": snapshot["huggingface"]["space_status"],
            "community_post_performed": False,
            "github_release_created": False,
            "mcp_registry_submission_performed": False,
            "actual_publish_performed": False,
        }
    else:
        payload = _template_payload(phase)
        path = TEMPLATE_PATHS[phase]
        if write_result:
            _write_json(path, payload)
        summary = {
            "phase": phase,
            "output_path": str(path).replace("\\", "/"),
            "public_beta_mcp_count": "not_checked",
            "github_stars": "not_checked",
            "github_open_issues": "not_checked",
            "hf_space_status": "not_checked",
            "community_post_performed": False,
            "github_release_created": False,
            "mcp_registry_submission_performed": False,
            "actual_publish_performed": False,
        }
    if write_result:
        _append_phase_log(phase, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AOI 72-hour public observation phase.")
    parser.add_argument("--phase", choices=sorted(VALID_PHASES), default="0h")
    args = parser.parse_args()
    result = run_public_observation_phase(args.phase)
    print(
        "public_observation_runner: "
        f"phase={result['phase']} "
        f"output={result['output_path']} "
        "community_post_performed=False"
    )


if __name__ == "__main__":
    main()
