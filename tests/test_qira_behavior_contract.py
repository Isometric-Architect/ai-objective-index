from ai_objective_index.portfolio.qira_behavior_contract import behavior_contract_detects_forbidden, build_behavior_contract
from ai_objective_index.portfolio.qira_pilot_packager import build_sample_task_packet


def test_qira_behavior_contract_blocks_forbidden_behavior():
    contract = build_behavior_contract(build_sample_task_packet())

    assert behavior_contract_detects_forbidden(contract, "deploy to production") is True
    assert behavior_contract_detects_forbidden(contract, "update docs only") is False
