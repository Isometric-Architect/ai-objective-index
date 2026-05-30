from ai_objective_index.agent_discovery_eval.public_discovery_smoke import run_public_discovery_smoke


def test_public_discovery_smoke_passes_with_pypi_and_registry_pass():
    result = run_public_discovery_smoke(
        pypi_smoke=lambda write_result=True: {
            "decision": "PASS_PYPI_PUBLIC_INSTALL_SMOKE",
            "verification_payload": {"version": "0.3.0a2"},
        },
        registry_smoke=lambda write_result=True: {
            "decision": "PASS_MCP_REGISTRY_PUBLIC_SMOKE",
            "matches": {"server_name": True},
        },
        write_result=False,
    )

    assert result["decision"] == "PASS_PUBLIC_DISCOVERY_SMOKE"
    assert result["external_llm_api_called"] is False
    assert result["publish_performed"] is False


def test_public_discovery_smoke_holds_registry_propagation():
    result = run_public_discovery_smoke(
        pypi_smoke=lambda write_result=True: {"decision": "PASS_PYPI_PUBLIC_INSTALL_SMOKE"},
        registry_smoke=lambda write_result=True: {"decision": "HOLD_REGISTRY_PROPAGATION"},
        write_result=False,
    )

    assert result["decision"] == "HOLD_REGISTRY_PROPAGATION"
