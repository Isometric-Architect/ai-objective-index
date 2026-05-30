from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack


def test_external_share_pack_manifest_generated():
    result = generate_external_share_pack(write_result=True)
    manifest = result["manifest"]
    assert manifest["schema"] == "ResidualOps_ExternalSafeSharePackManifest/v0.1"
    assert manifest["artifact_count"] >= 10
    assert all(item["safe_to_share_publicly"] is True for item in manifest["artifacts"])
