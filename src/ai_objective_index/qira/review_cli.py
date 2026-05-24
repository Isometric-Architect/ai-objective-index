from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .diff_classifier import classify_patch_paths
from .input_packet import QiraTaskPacket, sample_task_packet
from .packet_loader import QiraPacketError, build_report_from_packet, load_task_packet
from .test_command_contract import build_test_command_contract


OUTPUT_DIR = Path("public_launch") / "qira3"
SAMPLE_PACKET_PATH = OUTPUT_DIR / "QIRA3_SAMPLE_TASK_PACKET.json"
RELEASE_GATE_PATH = OUTPUT_DIR / "QIRA3_RELEASE_GATE_REPORT.json"
PATH_CLASSIFICATION_PATH = OUTPUT_DIR / "QIRA3_PATH_CLASSIFICATION_REPORT.json"
TEST_COMMAND_CONTRACT_PATH = OUTPUT_DIR / "QIRA3_TEST_COMMAND_CONTRACT.json"
REVIEW_RESULT_PATH = OUTPUT_DIR / "QIRA3_REVIEW_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "QIRA3_NEXT_STEPS.md"


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


def write_sample_packet() -> Path:
    packet = sample_task_packet()
    return _write_json(SAMPLE_PACKET_PATH, packet.model_dump(mode="json", by_alias=True))


def _decision_from_parts(release_decision: str, path_decision: str, command_decision: str) -> str:
    if release_decision.startswith("BLOCK") or path_decision.startswith("BLOCK") or command_decision.startswith("BLOCK"):
        return "BLOCK_QIRA3_REVIEW"
    if release_decision.startswith("HOLD") or path_decision.startswith("HOLD") or command_decision.startswith("HOLD"):
        return "HOLD_QIRA3_REVIEW"
    return "PASS_QIRA3_REVIEW"


def build_qira3_review(packet: QiraTaskPacket) -> dict[str, Any]:
    release_report = build_report_from_packet(packet)
    path_report = classify_patch_paths(packet.changed_files, packet.patch_diff, forbidden_changes=packet.forbidden_changes)
    command_contract = build_test_command_contract(packet.test_commands)
    decision = _decision_from_parts(release_report.decision_token, path_report.decision, command_contract.decision)
    return {
        "decision": decision,
        "release_gate_decision": release_report.decision_token,
        "path_classification_decision": path_report.decision,
        "test_command_contract_decision": command_contract.decision,
        "action_license": release_report.action_license.model_dump(mode="json", by_alias=True),
        "path_summary": {
            "changed_file_count": path_report.changed_file_count,
            "category_counts": path_report.category_counts,
            "risk_counts": path_report.risk_counts,
        },
        "test_command_summary": {
            "command_count": command_contract.command_count,
            "commands_executed": command_contract.commands_executed,
            "allowed_execution": command_contract.allowed_execution,
        },
        "external_actions_performed": False,
        "tests_executed_by_qira": False,
        "patch_applied": False,
        "deploy_performed": False,
        "token_printed": False,
        "_release_report": release_report,
        "_path_report": path_report,
        "_command_contract": command_contract,
    }


def run_qira3_review(input_path: str | Path, output_path: str | Path = RELEASE_GATE_PATH) -> dict[str, Any]:
    source = Path(input_path)
    try:
        packet = load_task_packet(_repo_root() / source if not source.is_absolute() else source)
        review = build_qira3_review(packet)
        release_report = review.pop("_release_report")
        path_report = review.pop("_path_report")
        command_contract = review.pop("_command_contract")
        report_destination = Path(output_path)
        if not report_destination.is_absolute():
            report_destination = _repo_root() / report_destination
        report_destination.parent.mkdir(parents=True, exist_ok=True)
        report_destination.write_text(json.dumps(release_report.model_dump(mode="json", by_alias=True), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        _write_json(PATH_CLASSIFICATION_PATH, path_report.model_dump(mode="json", by_alias=True))
        _write_json(TEST_COMMAND_CONTRACT_PATH, command_contract.model_dump(mode="json", by_alias=True))
    except QiraPacketError as exc:
        review = {
            "decision": "BLOCK_QIRA3_PACKET_INVALID",
            "error": str(exc),
            "external_actions_performed": False,
            "tests_executed_by_qira": False,
            "patch_applied": False,
            "deploy_performed": False,
            "token_printed": False,
        }
    _write_json(REVIEW_RESULT_PATH, review)
    _write_text(
        NEXT_STEPS_PATH,
        """# QIRA-3 Next Steps

1. Add richer diff statistics without exposing private heuristics.
2. Add optional project-owned test-command allowlists.
3. Add a GitHub Action wrapper that records command contracts before execution.
4. Keep execution, merge, deploy, and public readiness separately gated.

QIRA-3 classifies local packet metadata. It does not execute commands, apply patches, deploy code, contact external services, or handle tokens.
""",
    )
    return review


def run_sample() -> dict[str, Any]:
    write_sample_packet()
    return run_qira3_review(SAMPLE_PACKET_PATH, RELEASE_GATE_PATH)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run QIRA-3 local patch classification and test-command contract review.")
    parser.add_argument("--input", help="Path to a local QIRA task packet JSON file.")
    parser.add_argument("--output", default=str(RELEASE_GATE_PATH), help="Path for the release-gate report JSON.")
    parser.add_argument("--write-sample", action="store_true", help="Write a safe sample QIRA-3 packet.")
    parser.add_argument("--run-sample", action="store_true", help="Write and run the safe sample QIRA-3 packet.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.run_sample:
        result = run_sample()
    else:
        if args.write_sample:
            write_sample_packet()
        if not args.input:
            result = {"decision": "HOLD_QIRA3_PACKET_INPUT_REQUIRED", "external_actions_performed": False, "token_printed": False}
            _write_json(REVIEW_RESULT_PATH, result)
        else:
            result = run_qira3_review(args.input, args.output)
    print(f"qira_review_cli: {result['decision']}")


if __name__ == "__main__":
    main()
