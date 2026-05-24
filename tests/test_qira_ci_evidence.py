from ai_objective_index.qira.ci_evidence import (
    CiCheckResult,
    CiEvidencePacket,
    apply_ci_evidence_to_packet,
    build_qira6_ci_review,
    sample_ci_evidence_packet,
    validate_ci_evidence,
)
from ai_objective_index.qira.packet_generator import generate_packet_from_request, sample_generation_request


def _sample_packet():
    return generate_packet_from_request(sample_generation_request()).packet


def test_ci_evidence_pass_accepts_without_running_commands():
    evidence = sample_ci_evidence_packet("packet-1")

    result = validate_ci_evidence(evidence)

    assert result.decision == "PASS_CI_EVIDENCE_ACCEPTED"
    assert result.tests_passed is True
    assert result.commands_executed_by_qira is False
    assert result.github_api_used_by_qira is False
    assert result.can_authorize_merge is False
    assert result.can_authorize_deploy is False


def test_ci_evidence_failure_blocks():
    evidence = CiEvidencePacket(
        checks=[
            CiCheckResult(
                name="pytest",
                command="python -m pytest tests/test_example.py",
                status="fail",
                exit_code=1,
            )
        ]
    )

    result = validate_ci_evidence(evidence)

    assert result.decision == "BLOCK_CI_EVIDENCE_FAILED"
    assert result.tests_passed is False


def test_ci_evidence_unsafe_command_blocks():
    evidence = CiEvidencePacket(
        checks=[
            CiCheckResult(
                name="publish",
                command="python -m twine upload dist/example.whl",
                status="pass",
                exit_code=0,
            )
        ]
    )

    result = validate_ci_evidence(evidence)

    assert result.decision == "BLOCK_CI_COMMAND_UNSAFE"


def test_ci_evidence_token_like_text_blocks():
    evidence = CiEvidencePacket(
        checks=[
            CiCheckResult(
                name="pytest",
                command="python -m pytest tests/test_example.py",
                status="pass",
                exit_code=0,
                summary="token=abcdefghijklmnopqrstuvwxyz123456",
            )
        ]
    )

    result = validate_ci_evidence(evidence)

    assert result.decision == "BLOCK_SECRET_IN_EVIDENCE"


def test_apply_ci_evidence_sets_tests_passed_only_when_accepted():
    packet = _sample_packet()
    evidence = sample_ci_evidence_packet(packet.resolved_packet_id())
    validation = validate_ci_evidence(evidence)

    augmented = apply_ci_evidence_to_packet(packet, evidence, validation)

    assert augmented.tests_passed is True
    assert augmented.evidence_origin == "ci_fixture"
    assert "ci_evidence_id" in augmented.model_dump()


def test_qira6_review_turns_sample_into_scoped_pass():
    packet = _sample_packet()
    evidence = sample_ci_evidence_packet(packet.resolved_packet_id())

    result = build_qira6_ci_review(packet, evidence)

    assert result.decision == "PASS_QIRA6_REVIEW"
    assert result.release_gate_review["release_gate_decision"] == "PASS_CONTRACT_SCOPED"
    assert result.commands_executed_by_qira is False
    assert result.patch_applied is False
