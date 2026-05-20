from ai_objective_index.vnext import ProbeCard


def test_vnext_probe_card_defaults_to_not_run():
    probe = ProbeCard(
        probe_id="probe-package-import",
        target_capability="cap-local-install-smoke",
        objective_scope="python_package_release_audit",
        expected_behavior="import succeeds without network",
    )

    payload = probe.model_dump(by_alias=True)
    assert payload["schema"] == "aoi.vnext.probe_card.v0_3"
    assert payload["pass_fail"] == "not_run"
    assert payload["sandbox_policy"] == "local_or_read_only"
