from ai_objective_index.portfolio.external_share_pack_archive import run_archive
from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack


def test_external_share_archive_dry_run_does_not_build():
    generate_external_share_pack(write_result=True)
    result = run_archive(dry_run=True, build=False, write_result=True)
    assert result["result_token"] == "DRY_RUN_ONLY"
    assert result["archive_built"] is False


def test_external_share_archive_build_result_shape():
    generate_external_share_pack(write_result=True)
    result = run_archive(dry_run=False, build=True, write_result=False)
    assert result["result_token"] in {"ARCHIVE_BUILT", "HOLD_ARCHIVE_NOT_BUILT"}
    if result["archive_built"]:
        assert result["archive_sha256"]
