from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .ci_evidence import (
    CiEvidencePacket,
    build_qira6_ci_review,
    sample_ci_evidence_packet,
    validate_ci_evidence,
)
from .packet_generator import generate_packet_from_request, sample_generation_request
from .packet_loader import load_task_packet


OUTPUT_DIR = Path("public_launch") / "qira6"
SAMPLE_PACKET_PATH = OUTPUT_DIR / "QIRA6_SAMPLE_TASK_PACKET.json"
SAMPLE_CI_EVIDENCE_PATH = OUTPUT_DIR / "QIRA6_SAMPLE_CI_EVIDENCE.json"
VALIDATION_RESULT_PATH = OUTPUT_DIR / "QIRA6_VALIDATION_RESULT.json"
AUGMENTED_PACKET_PATH = OUTPUT_DIR / "QIRA6_AUGMENTED_TASK_PACKET.json"
REVIEW_RESULT_PATH = OUTPUT_DIR / "QIRA6_REVIEW_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "QIRA6_NEXT_STEPS.md"


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


def _load_ci_evidence(path: str | Path) -> CiEvidencePacket:
    source = Path(path)
    if not source.is_absolute():
        source = _repo_root() / source
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"CI evidence packet not found: {source}")
    if source.suffix.lower() != ".json":
        raise ValueError("CI evidence packet must be JSON.")
    if source.stat().st_size > 1_000_000:
        raise ValueError("CI evidence packet is too large for QIRA-6 local intake.")
    return CiEvidencePacket.model_validate_json(source.read_text(encoding="utf-8"))


def write_next_steps() -> Path:
    return _write_text(
        NEXT_STEPS_PATH,
        """# QIRA-6 Next Steps

1. Let repository CI produce a QIRA CI evidence JSON artifact after tests/static checks run.
2. Feed that artifact into QIRA-6 together with the QIRA task packet.
3. Keep QIRA as an evidence reviewer, not a command executor.
4. Add an opt-in workflow that uploads packet and evidence artifacts only when the repository owner enables it.

QIRA-6 does not run tests, call GitHub APIs, inspect live CI, apply patches, merge, deploy, upload, publish, handle tokens, certify security, guarantee quality, or authorize production actions.
""",
    )


def write_qira6_review(packet, evidence: CiEvidencePacket) -> dict[str, Any]:
    validation = validate_ci_evidence(evidence)
    review_result = build_qira6_ci_review(packet, evidence)
    _write_json(VALIDATION_RESULT_PATH, validation.model_dump(mode="json", by_alias=True))
    _write_json(AUGMENTED_PACKET_PATH, review_result.augmented_packet.model_dump(mode="json", by_alias=True))
    _write_json(REVIEW_RESULT_PATH, review_result.model_dump(mode="json", by_alias=True))
    write_next_steps()
    return {
        "decision": review_result.decision,
        "validation_decision": validation.decision,
        "release_gate_decision": review_result.release_gate_review.get("release_gate_decision"),
        "external_actions_performed": False,
        "commands_executed_by_qira": False,
        "github_api_used_by_qira": False,
        "patch_applied": False,
        "deploy_performed": False,
        "token_printed": False,
    }


def run_sample() -> dict[str, Any]:
    generated = generate_packet_from_request(sample_generation_request())
    evidence = sample_ci_evidence_packet(generated.packet.resolved_packet_id())
    _write_json(SAMPLE_PACKET_PATH, generated.packet.model_dump(mode="json", by_alias=True))
    _write_json(SAMPLE_CI_EVIDENCE_PATH, evidence.model_dump(mode="json", by_alias=True))
    return write_qira6_review(generated.packet, evidence)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review externally supplied CI evidence for a QIRA task packet.")
    parser.add_argument("--run-sample", action="store_true", help="Write and review a safe QIRA-6 sample.")
    parser.add_argument("--packet", help="Path to a local QIRA task packet JSON file.")
    parser.add_argument("--evidence", help="Path to a local QIRA CI evidence JSON file.")
    parser.add_argument("--write-sample", action="store_true", help="Write sample packet and CI evidence files.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.run_sample:
        result = run_sample()
    else:
        if args.write_sample:
            generated = generate_packet_from_request(sample_generation_request())
            evidence = sample_ci_evidence_packet(generated.packet.resolved_packet_id())
            _write_json(SAMPLE_PACKET_PATH, generated.packet.model_dump(mode="json", by_alias=True))
            _write_json(SAMPLE_CI_EVIDENCE_PATH, evidence.model_dump(mode="json", by_alias=True))
        if not args.packet or not args.evidence:
            result = {
                "decision": "HOLD_QIRA6_PACKET_AND_EVIDENCE_REQUIRED",
                "external_actions_performed": False,
                "commands_executed_by_qira": False,
                "github_api_used_by_qira": False,
                "token_printed": False,
            }
            _write_json(REVIEW_RESULT_PATH, result)
        else:
            packet_path = Path(args.packet)
            if not packet_path.is_absolute():
                packet_path = _repo_root() / packet_path
            result = write_qira6_review(load_task_packet(packet_path), _load_ci_evidence(args.evidence))
    print(f"qira_ci_evidence_cli: {result['decision']} validation={result.get('validation_decision', 'not_checked')}")


if __name__ == "__main__":
    main()
