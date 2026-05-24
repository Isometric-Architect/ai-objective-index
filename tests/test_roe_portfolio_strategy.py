from ai_objective_index.roe_portfolio_strategy import build_portfolio_strategy


def test_strategy_locks_sequence_without_building_all_three_at_once():
    result = build_portfolio_strategy()

    assert result["decision"] == "PASS_PORTFOLIO_SEQUENCE_LOCKED"
    assert result["selected_next_package"] == "QIRA-1"
    sequence = [item["product"] for item in result["implementation_sequence"]]
    assert sequence[1:] == ["QIRA-Code ReleaseGate", "AgentSec Gate", "DataCapsule / AIDREG Engine"]
    assert result["external_actions_performed"] is False


def test_strategy_keeps_private_kernel_reserved():
    result = build_portfolio_strategy()

    reserved = result["common_kernel"]["private_kernel_reserved"]
    assert "ranking-weight values" in reserved
    assert "provider trust priors" in reserved
    assert "security certified" in result["must_not_claim"]
