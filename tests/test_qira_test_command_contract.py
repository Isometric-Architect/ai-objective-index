from ai_objective_index.qira.test_command_contract import build_test_command_contract, classify_test_command


def test_safe_pytest_command_records_without_execution():
    record = classify_test_command("python -m pytest tests/test_qira_task_cli.py")

    assert record.risk == "LOW"
    assert record.executed_by_qira is False


def test_network_or_publish_command_blocks():
    contract = build_test_command_contract(["curl https://example.com", "python -m twine upload dist/*"])

    assert contract.decision == "BLOCK_TEST_COMMAND_CONTRACT"
    assert contract.commands_executed is False
    assert contract.external_actions_performed is False


def test_install_command_holds_for_review():
    contract = build_test_command_contract(["python -m pip install -r requirements.txt"])

    assert contract.decision == "HOLD_TEST_COMMAND_REVIEW"
    assert contract.hold_reasons


def test_missing_commands_hold_not_crash():
    contract = build_test_command_contract([])

    assert contract.decision == "HOLD_TEST_COMMAND_MISSING"
    assert contract.command_count == 0
