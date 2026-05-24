from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .packet_generator import (
    QiraPacketGenerationRequest,
    generate_packet_from_request,
    sample_generation_request,
    sample_pr_diff,
)
from .review_cli import build_qira3_review


OUTPUT_DIR = Path("public_launch") / "qira5"
SAMPLE_DIFF_PATH = OUTPUT_DIR / "QIRA5_SAMPLE_PR_DIFF.patch"
GENERATED_PACKET_PATH = OUTPUT_DIR / "QIRA5_GENERATED_TASK_PACKET.json"
GENERATION_RESULT_PATH = OUTPUT_DIR / "QIRA5_PACKET_GENERATION_RESULT.json"
REVIEW_RESULT_PATH = OUTPUT_DIR / "QIRA5_REVIEW_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "QIRA5_NEXT_STEPS.md"


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


def _read_diff_file(path: str | Path) -> str:
    source = Path(path)
    if not source.is_absolute():
        source = _repo_root() / source
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Diff file not found: {source}")
    if source.stat().st_size > 1_000_000:
        raise ValueError("Diff file is too large for QIRA-5 local intake.")
    return source.read_text(encoding="utf-8", errors="ignore")


def _split_changed_files(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _public_generation_payload(result) -> dict[str, Any]:
    return {
        "schema": result.schema_id,
        "decision": result.decision,
        "changed_files": result.changed_files,
        "inferred_expected_behavior": result.inferred_expected_behavior,
        "path_classification_decision": result.path_classification_decision,
        "path_classification": result.path_classification.model_dump(mode="json", by_alias=True),
        "known_limits": result.known_limits,
        "external_actions_performed": result.external_actions_performed,
        "git_command_executed": result.git_command_executed,
        "github_api_used": result.github_api_used,
        "tests_executed": result.tests_executed,
        "patch_applied": result.patch_applied,
        "token_printed": result.token_printed,
        "generated_at": result.generated_at,
    }


def _review_packet(packet) -> dict[str, Any]:
    review = build_qira3_review(packet)
    review.pop("_release_report", None)
    review.pop("_path_report", None)
    review.pop("_command_contract", None)
    return review


def write_next_steps() -> Path:
    return _write_text(
        NEXT_STEPS_PATH,
        """# QIRA-5 Next Steps

1. Wire this local packet generator into the existing reusable GitHub Action wrapper.
2. Let CI provide changed-file lists or diff artifacts explicitly instead of letting QIRA call GitHub APIs.
3. Add project-owned evidence fields for test results after commands are executed by the repository's normal CI.
4. Keep merge, deploy, package upload, registry submission, and public readiness claims behind separate gates.

QIRA-5 generates conservative local task packets. It does not call GitHub APIs, run git commands, apply patches, execute tests, deploy, upload, publish, handle tokens, or certify code quality/security.
""",
    )


def generate_and_write(request: QiraPacketGenerationRequest, review: bool = True) -> dict[str, Any]:
    result = generate_packet_from_request(request)
    _write_json(GENERATED_PACKET_PATH, result.packet.model_dump(mode="json", by_alias=True))
    _write_json(GENERATION_RESULT_PATH, _public_generation_payload(result))
    review_payload: dict[str, Any] = {
        "decision": "HOLD_QIRA5_REVIEW_NOT_REQUESTED",
        "external_actions_performed": False,
        "git_command_executed": False,
        "github_api_used": False,
        "tests_executed_by_qira": False,
        "patch_applied": False,
        "token_printed": False,
    }
    if review:
        review_payload = _review_packet(result.packet)
        review_payload["qira5_generation_decision"] = result.decision
        review_payload["git_command_executed"] = False
        review_payload["github_api_used"] = False
    _write_json(REVIEW_RESULT_PATH, review_payload)
    write_next_steps()
    return {
        "generation_decision": result.decision,
        "review_decision": review_payload["decision"],
        "changed_file_count": len(result.changed_files),
        "external_actions_performed": False,
        "git_command_executed": False,
        "github_api_used": False,
        "tests_executed_by_qira": False,
        "patch_applied": False,
        "token_printed": False,
    }


def run_sample() -> dict[str, Any]:
    _write_text(SAMPLE_DIFF_PATH, sample_pr_diff())
    return generate_and_write(sample_generation_request(), review=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a QIRA task packet from local PR diff or changed-file metadata.")
    parser.add_argument("--run-sample", action="store_true", help="Write and review a safe local QIRA-5 sample.")
    parser.add_argument("--diff-file", help="Path to a local unified diff file. QIRA reads it only; it does not run git.")
    parser.add_argument("--changed-files", help="Comma-separated repository-relative changed files.")
    parser.add_argument("--task", default="Generate a conservative QIRA task packet from local changed-file metadata.")
    parser.add_argument("--patch-summary", default="Generated from local diff or changed-file metadata.")
    parser.add_argument("--test-command", action="append", default=[], help="Record a project-owned test/static-check command without executing it.")
    parser.add_argument("--tests-passed", action="store_true", help="Record externally supplied test pass evidence. QIRA-5 still does not execute tests.")
    parser.add_argument("--test-summary", default="")
    parser.add_argument("--declared-claim", action="append", default=[])
    parser.add_argument("--requested-action", default="pr_open", choices=["patch_draft", "pr_open", "merge", "deploy", "public_claim"])
    parser.add_argument("--no-review", action="store_true", help="Skip local QIRA-3 review over the generated packet.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.run_sample:
        result = run_sample()
    else:
        patch_diff = _read_diff_file(args.diff_file) if args.diff_file else ""
        request = QiraPacketGenerationRequest(
            task=args.task,
            patch_summary=args.patch_summary,
            changed_files=_split_changed_files(args.changed_files),
            patch_diff=patch_diff,
            test_commands=args.test_command,
            tests_passed=args.tests_passed,
            test_summary=args.test_summary,
            declared_claims=args.declared_claim,
            requested_action=args.requested_action,
        )
        result = generate_and_write(request, review=not args.no_review)
    print(f"qira_pr_packet_cli: {result['generation_decision']} review={result['review_decision']}")


if __name__ == "__main__":
    main()
