from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .input_packet import sample_task_packet
from .packet_loader import QiraPacketError, build_report_from_packet_file


OUTPUT_DIR = Path("public_launch") / "qira2"
SAMPLE_PACKET_PATH = OUTPUT_DIR / "QIRA2_SAMPLE_TASK_PACKET.json"
DEFAULT_REPORT_PATH = OUTPUT_DIR / "QIRA2_RELEASE_GATE_REPORT.json"
INTAKE_RESULT_PATH = OUTPUT_DIR / "QIRA2_PACKET_INTAKE_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "QIRA2_NEXT_STEPS.md"


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


def run_task_packet_cli(input_path: str | Path, output_path: str | Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    source = Path(input_path)
    relative_output = Path(output_path)
    if relative_output.is_absolute():
        destination = relative_output
    else:
        destination = _repo_root() / relative_output
    try:
        report = build_report_from_packet_file(_repo_root() / source if not source.is_absolute() else source)
        payload = report.model_dump(mode="json", by_alias=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        result = {
            "decision": "PASS_QIRA_PACKET_INTAKE",
            "input_path": str(source).replace("\\", "/"),
            "output_path": str(relative_output).replace("\\", "/"),
            "decision_token": report.decision_token,
            "action_license": report.action_license.model_dump(mode="json", by_alias=True),
            "external_actions_performed": False,
            "tests_executed_by_qira": False,
            "deploy_performed": False,
            "token_printed": False,
        }
    except QiraPacketError as exc:
        result = {
            "decision": "BLOCK_QIRA_PACKET_INVALID",
            "input_path": str(source).replace("\\", "/"),
            "output_path": str(relative_output).replace("\\", "/"),
            "error": str(exc),
            "external_actions_performed": False,
            "tests_executed_by_qira": False,
            "deploy_performed": False,
            "token_printed": False,
        }
    _write_json(INTAKE_RESULT_PATH, result)
    _write_text(
        NEXT_STEPS_PATH,
        """# QIRA-2 Next Steps

1. Add a `qira packet` command group with stricter user-facing help.
2. Add patch diff summary and path classification reports.
3. Add optional project-owned test command recording, still without executing arbitrary tools by default.
4. Add a GitHub Action wrapper once packet intake is stable.

QIRA-2 reads local packet files and writes local receipts. It does not execute tests, deploy code, contact external services, request tokens, or certify a patch.
""",
    )
    return result


def run_sample() -> dict[str, Any]:
    write_sample_packet()
    return run_task_packet_cli(SAMPLE_PACKET_PATH, DEFAULT_REPORT_PATH)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run local QIRA task packet intake without external execution.")
    parser.add_argument("--input", help="Path to a local QIRA task packet JSON file.")
    parser.add_argument("--output", default=str(DEFAULT_REPORT_PATH), help="Path for the release-gate report JSON.")
    parser.add_argument("--write-sample", action="store_true", help="Write a safe sample QIRA task packet.")
    parser.add_argument("--run-sample", action="store_true", help="Write and run the safe sample QIRA task packet.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.run_sample:
        result = run_sample()
    else:
        if args.write_sample:
            write_sample_packet()
        if not args.input:
            result = {"decision": "HOLD_QIRA_PACKET_INPUT_REQUIRED", "external_actions_performed": False, "token_printed": False}
            _write_json(INTAKE_RESULT_PATH, result)
        else:
            result = run_task_packet_cli(args.input, args.output)
    print(f"qira_task_cli: {result['decision']}")


if __name__ == "__main__":
    main()
