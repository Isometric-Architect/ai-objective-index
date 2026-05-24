import json
from pathlib import Path

from ai_objective_index.qira.pr_packet_cli import (
    GENERATED_PACKET_PATH,
    GENERATION_RESULT_PATH,
    REVIEW_RESULT_PATH,
    generate_and_write,
    run_sample,
)
from ai_objective_index.qira.packet_generator import QiraPacketGenerationRequest


def test_qira5_run_sample_writes_outputs():
    result = run_sample()

    assert result["generation_decision"] == "PASS_QIRA_PACKET_GENERATED"
    assert result["review_decision"] == "HOLD_QIRA3_REVIEW"
    assert Path(GENERATED_PACKET_PATH).exists()
    assert Path(GENERATION_RESULT_PATH).exists()
    assert Path(REVIEW_RESULT_PATH).exists()

    generation = json.loads(Path(GENERATION_RESULT_PATH).read_text(encoding="utf-8"))
    assert generation["git_command_executed"] is False
    assert generation["github_api_used"] is False
    assert generation["tests_executed"] is False


def test_qira5_generate_and_write_from_changed_files():
    request = QiraPacketGenerationRequest(
        task="Update local docs and parser.",
        changed_files=["src/parser.py", "docs/parser.md"],
        test_commands=["python -m pytest tests/test_parser.py"],
        tests_passed=True,
        test_summary="External CI fixture passed.",
        evidence_origin="ci_fixture",
    )

    result = generate_and_write(request, review=True)

    assert result["generation_decision"] == "PASS_QIRA_PACKET_GENERATED"
    assert result["review_decision"] == "PASS_QIRA3_REVIEW"
    assert result["external_actions_performed"] is False


def test_qira5_generate_and_write_blocks_secret_path():
    request = QiraPacketGenerationRequest(
        task="Review secret path.",
        changed_files=["secrets/prod.key"],
    )

    result = generate_and_write(request, review=True)

    assert result["generation_decision"] == "BLOCK_FORBIDDEN_PATH"
    assert result["review_decision"] == "BLOCK_QIRA3_REVIEW"
