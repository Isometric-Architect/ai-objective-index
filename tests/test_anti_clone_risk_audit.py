from ai_objective_index import anti_clone_risk_audit as audit


def test_public_beta_with_private_kernel_split_is_acceptable_or_hold():
    result = audit.assess_clone_risk(private_kernel_split=True, full_private_kernel_exposed=False)

    assert result["decision"] in {"PASS_ACCEPTABLE_PUBLIC_BETA_RISK", "HOLD_LICENSE_REVIEW"}


def test_exposed_full_private_kernel_blocks():
    result = audit.assess_clone_risk(full_private_kernel_exposed=True)

    assert result["decision"] == "BLOCK_OVEREXPOSED_CORE_LOGIC"
