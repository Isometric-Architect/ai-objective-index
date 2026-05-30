from ai_objective_index.agent_discovery_eval import agent_discovery_3_gate
from ai_objective_index.agent_discovery_eval.agent_eval_report import write_eval_support_artifacts
from ai_objective_index.agent_discovery_eval.ordinary_agent_prompt_eval import run_ordinary_agent_prompt_eval


def test_agent_discovery_3_gate_passes_on_current_artifacts(monkeypatch):
    run_ordinary_agent_prompt_eval(write_result=True)
    write_eval_support_artifacts()
    monkeypatch.setattr(agent_discovery_3_gate, "_artifact_text", lambda: "{}")
    monkeypatch.setattr(agent_discovery_3_gate, "ARTIFACT_PATHS", [])
    monkeypatch.setattr(
        agent_discovery_3_gate,
        "read_json",
        lambda path: {
            "decision": "PASS_PYPI_PUBLIC_INSTALL_SMOKE"
            if "PYPI" in str(path)
            else "PASS_MCP_REGISTRY_PUBLIC_SMOKE"
            if "MCP" in str(path)
            else "PASS_PUBLIC_DISCOVERY_SMOKE"
            if "PUBLIC_DISCOVERY" in str(path)
            else {"aoi_guided_total_score": 100, "naive_total_score": 10},
        },
    )
    result = agent_discovery_3_gate.run_agent_discovery_3_gate(write_result=False)

    assert result["decision"] == "PASS_AGENT_PUBLIC_DISCOVERY_AND_PROMPT_EVAL_READY"


def test_agent_discovery_3_gate_blocks_overclaim(monkeypatch):
    monkeypatch.setattr(agent_discovery_3_gate, "_artifact_text", lambda: "this is security certified")

    result = agent_discovery_3_gate.run_agent_discovery_3_gate(write_result=False)

    assert result["decision"] == "BLOCK_OVERCLAIM"


def test_agent_discovery_3_gate_blocks_private_kernel_fixture(monkeypatch):
    monkeypatch.setattr(agent_discovery_3_gate, "_artifact_text", lambda: "ranking_weights: 0.1")

    result = agent_discovery_3_gate.run_agent_discovery_3_gate(write_result=False)

    assert result["decision"] == "BLOCK_PRIVATE_KERNEL_EXPOSURE"
