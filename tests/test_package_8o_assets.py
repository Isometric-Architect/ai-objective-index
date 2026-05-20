from pathlib import Path

from ai_objective_index.github_release_manager import create_release_notes
from ai_objective_index.launch_wave1_report import run_launch_wave1_report


def test_package_8o_assets_exist():
    create_release_notes()
    run_launch_wave1_report(write_result=True)

    assert Path("docs/package_8o_public_beta_launch_wave1.md").exists()
    assert Path("docs/github_release_public_beta.md").exists()
    assert Path("docs/conservative_community_feedback_launch.md").exists()
    assert Path("docs/mcp_registry_submission_gate.md").exists()
    assert Path("public_launch/wave1/GITHUB_RELEASE_NOTES_v0_2_0_public_beta.md").exists()
    assert Path("public_launch/wave1/POST_LAUNCH_MONITORING_CHECKLIST.md").exists()
