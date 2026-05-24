from ai_objective_index.qira.packet_generator import (
    QiraPacketGenerationRequest,
    generate_packet_from_request,
    sample_generation_request,
)


def test_generate_packet_from_diff_derives_changed_files():
    result = generate_packet_from_request(sample_generation_request())

    assert result.decision == "PASS_QIRA_PACKET_GENERATED"
    assert "src/ai_objective_index/qira/packet_generator.py" in result.changed_files
    assert result.packet.schema_id == "QIRA_TaskPacket/v0.1"
    assert result.git_command_executed is False
    assert result.github_api_used is False
    assert result.tests_executed is False


def test_generate_packet_without_files_holds():
    request = QiraPacketGenerationRequest(task="Review a patch without changed-file metadata.")

    result = generate_packet_from_request(request)

    assert result.decision == "HOLD_NO_CHANGED_FILES"
    assert result.path_classification_decision == "HOLD_NO_CHANGED_FILES"
    assert result.patch_applied is False


def test_generate_packet_blocks_secret_path():
    request = QiraPacketGenerationRequest(
        task="Review accidental secret-file change.",
        changed_files=[".env"],
    )

    result = generate_packet_from_request(request)

    assert result.decision == "BLOCK_FORBIDDEN_PATH"
    assert result.path_classification_decision == "BLOCK_PATH_CLASSIFICATION"


def test_generate_packet_holds_dependency_or_ci_path():
    request = QiraPacketGenerationRequest(
        task="Review packaging metadata update.",
        changed_files=["pyproject.toml", ".github/workflows/ci.yml"],
    )

    result = generate_packet_from_request(request)

    assert result.decision == "HOLD_PATH_REVIEW"
    assert result.path_classification_decision == "HOLD_PATH_REVIEW"


def test_generate_packet_does_not_inflate_test_command_record():
    request = QiraPacketGenerationRequest(
        task="Review local parser change.",
        changed_files=["src/parser.py", "tests/test_parser.py"],
        test_commands=["python -m pytest tests/test_parser.py"],
    )

    result = generate_packet_from_request(request)

    assert result.packet.tests_passed is False
    assert result.packet.test_commands == ["python -m pytest tests/test_parser.py"]
    assert "Do not deploy" in result.packet.expected_behavior[-1]
