from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack


def test_external_share_pack_checksums_generated():
    result = generate_external_share_pack(write_result=True)
    checksums = result["checksums"]
    assert checksums["schema"] == "ResidualOps_ExternalSafeSharePackChecksums/v0.1"
    assert checksums["checksum_count"] >= 10
    assert all(len(value) == 64 for value in checksums["checksums"].values())
