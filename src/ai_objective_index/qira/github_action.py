from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .input_packet import sample_task_packet
from .review_cli import build_qira3_review
from .packet_loader import QiraPacketError, load_task_packet


OUTPUT_DIR = Path("public_launch") / "qira4"
DEFAULT_PACKET_PATH = OUTPUT_DIR / "QIRA4_SAMPLE_ACTION_PACKET.json"
ACTION_RESULT_PATH = OUTPUT_DIR / "QIRA4_GITHUB_ACTION_DRY_RUN_RESULT.json"
ACTION_SUMMARY_PATH = OUTPUT_DIR / "QIRA4_GITHUB_ACTION_SUMMARY.md"
ACTION_MANIFEST_AUDIT_PATH = OUTPUT_DIR / "QIRA4_ACTION_MANIFEST_AUDIT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "QIRA4_NEXT_STEPS.md"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def write_sample_action_packet() -> Path:
    packet = sample_task_packet()
    return _write_json(DEFAULT_PACKET_PATH, packet.model_dump(mode="json", by_alias=True))


def _summary_markdown(result: dict[str, Any]) -> str:
    action = result.get("action_license", {})
    path_summary = result.get("path_summary", {})
    command_summary = result.get("test_command_summary", {})
    return f"""# QIRA ReleaseGate Dry Run

Decision: `{result.get('decision')}`

| Field | Value |
| --- | --- |
| Release gate | `{result.get('release_gate_decision')}` |
| Path classification | `{result.get('path_classification_decision')}` |
| Test command contract | `{result.get('test_command_contract_decision')}` |
| Patch draft | `{action.get('patch_draft')}` |
| PR open | `{action.get('pr_open')}` |
| Merge | `{action.get('merge')}` |
| Deploy | `{action.get('deploy')}` |
| Changed files | `{path_summary.get('changed_file_count')}` |
| Commands recorded | `{command_summary.get('command_count')}` |
| Commands executed by QIRA | `{command_summary.get('commands_executed')}` |

QIRA dry run did not apply patches, execute project commands, deploy code, contact external services, or handle tokens.
"""


def _append_github_summary(text: str, github_step_summary: str | None = None) -> bool:
    target = github_step_summary or os.environ.get("GITHUB_STEP_SUMMARY", "")
    if not target:
        return False
    try:
        with Path(target).open("a", encoding="utf-8") as handle:
            handle.write(text + "\n")
    except OSError:
        return False
    return True


def run_github_action_dry_run(
    input_path: str | Path | None = None,
    output_dir: str | Path = OUTPUT_DIR,
    write_sample: bool = False,
    github_step_summary: str | None = None,
) -> dict[str, Any]:
    output_base = Path(output_dir)
    if write_sample or input_path is None:
        packet_path = write_sample_action_packet()
    else:
        packet_path = Path(input_path)
        if not packet_path.is_absolute():
            packet_path = _repo_root() / packet_path
    try:
        packet = load_task_packet(packet_path)
        review = build_qira3_review(packet)
        review.pop("_release_report", None)
        review.pop("_path_report", None)
        review.pop("_command_contract", None)
        result = {
            **review,
            "decision": "PASS_QIRA_ACTION_DRY_RUN" if review["decision"].startswith("PASS") else review["decision"].replace("QIRA3", "QIRA_ACTION"),
            "input_path": str(packet_path).replace("\\", "/"),
            "output_dir": str(output_base).replace("\\", "/"),
            "github_action_wrapper": True,
            "workflow_auto_enabled": False,
            "external_actions_performed": False,
            "project_commands_executed": False,
            "patch_applied": False,
            "deploy_performed": False,
            "token_printed": False,
        }
    except QiraPacketError as exc:
        result = {
            "decision": "BLOCK_QIRA_ACTION_PACKET_INVALID",
            "input_path": str(packet_path).replace("\\", "/"),
            "output_dir": str(output_base).replace("\\", "/"),
            "error": str(exc),
            "github_action_wrapper": True,
            "workflow_auto_enabled": False,
            "external_actions_performed": False,
            "project_commands_executed": False,
            "patch_applied": False,
            "deploy_performed": False,
            "token_printed": False,
        }
    result_path = output_base / "QIRA4_GITHUB_ACTION_DRY_RUN_RESULT.json"
    summary_path = output_base / "QIRA4_GITHUB_ACTION_SUMMARY.md"
    summary_text = _summary_markdown(result)
    _write_json(result_path, result)
    _write_text(summary_path, summary_text)
    _append_github_summary(summary_text, github_step_summary=github_step_summary)
    _write_text(
        NEXT_STEPS_PATH,
        """# QIRA-4 Next Steps

1. Add a real repository fixture packet generated from a pull request diff.
2. Add project-owned allowlist support before any command execution is considered.
3. Keep the default GitHub Action wrapper in dry-run mode.
4. Add active workflow only when the repository owner intentionally enables it.

QIRA-4 provides a reusable action wrapper. It does not auto-enable a workflow, execute project commands, deploy code, or handle tokens.
""",
    )
    return result


def audit_action_manifest() -> dict[str, Any]:
    path = _repo_root() / ".github" / "actions" / "qira-releasegate-dry-run" / "action.yml"
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    forbidden = ["twine upload", "mcp-publisher publish", "git push", "curl ", "wget ", "gh release"]
    findings = [item for item in forbidden if item.lower() in text.lower()]
    result = {
        "decision": "PASS_QIRA_ACTION_MANIFEST_SAFE" if path.exists() and not findings else "BLOCK_QIRA_ACTION_MANIFEST_UNSAFE",
        "manifest_exists": path.exists(),
        "forbidden_command_findings": findings,
        "workflow_auto_enabled": False,
        "external_actions_performed": False,
        "token_printed": False,
    }
    _write_json(ACTION_MANIFEST_AUDIT_PATH, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run QIRA GitHub Action dry-run wrapper locally.")
    parser.add_argument("--input", help="Path to local QIRA task packet JSON.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Directory for QIRA action dry-run outputs.")
    parser.add_argument("--write-sample", action="store_true", help="Write and use a safe sample QIRA action packet.")
    parser.add_argument("--audit-manifest", action="store_true", help="Audit the local action.yml manifest.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_manifest:
        result = audit_action_manifest()
        print(f"qira_action_manifest_audit: {result['decision']}")
        return
    result = run_github_action_dry_run(args.input, args.output_dir, write_sample=args.write_sample)
    print(f"qira_github_action_dry_run: {result['decision']}")


if __name__ == "__main__":
    main()
