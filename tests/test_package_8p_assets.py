from pathlib import Path

from ai_objective_index.community_manual_queue import write_community_manual_queue
from ai_objective_index.pypi_upload_instructions import write_pypi_upload_instructions


def test_package_8p_assets_exist():
    write_pypi_upload_instructions()
    write_community_manual_queue()

    assert Path("docs/package_8p_mcp_registry_pypi_readiness.md").exists()
    assert Path("docs/pypi_publish_readiness.md").exists()
    assert Path("docs/mcp_registry_pypi_path.md").exists()
    assert Path("docs/community_manual_post_queue.md").exists()
    assert Path("public_launch/wave2/TESTPYPI_UPLOAD_INSTRUCTIONS.md").exists()
    assert Path("public_launch/wave2/COMMUNITY_MANUAL_POST_QUEUE.md").exists()
    assert Path("public_launch/wave2/WAVE2_SUMMARY.md").exists()
