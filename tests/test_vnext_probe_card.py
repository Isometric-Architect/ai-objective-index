from ai_objective_index.vnext import ProbeCard


def test_vnext_probe_card_is_local_only_probe():
    probe = ProbeCard(
        probe_id="probe-package-import",
        target_capability="cap-local-install-smoke",
        objective_scope="python_package_release_audit",
        expected_behavior="import succeeds without network",
    )

    payload = probe.model_dump(by_alias=True)
    assert payload["schema"] == "AOI_ProbeCard/v0.1"
    assert payload["capability_id"] == "cap-local-install-smoke"
    assert payload["sandbox_policy"]["no_network"] is True
    assert payload["sandbox_policy"]["no_external_tool_execution"] is True
