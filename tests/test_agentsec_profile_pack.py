from ai_objective_index.agentsec.profile_pack import build_profile_pack, write_profile_pack


def test_agentsec4_profile_pack_has_public_safe_profiles():
    result = build_profile_pack()

    assert result["decision"] == "PASS_AGENTSEC4_PROFILE_PACK_READY"
    assert result["profile_count"] >= 5
    assert result["external_actions_performed"] is False
    assert result["can_certify_security"] is False
    assert "exact thresholds" in result["private_kernel_reserved"]


def test_agentsec4_profile_pack_writes_outputs():
    result = write_profile_pack()

    assert result["decision"] == "PASS_AGENTSEC4_PROFILE_PACK_READY"
