import json
from pathlib import Path

from ai_objective_index.launch_wave1_report import run_launch_wave1_report


def _write(path: str, payload: dict):
    full = Path(path)
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(json.dumps(payload), encoding="utf-8")


def test_launch_wave1_report_includes_states():
    _write("public_launch/wave1/GITHUB_RELEASE_RESULT.json", {"release_created": True, "url": "https://example.test/release"})
    _write("public_launch/wave1/COMMUNITY_FEEDBACK_POST_RESULT.json", {"hf_discussion_created": False, "github_discussion_created": False})
    _write("public_launch/wave1/MCP_REGISTRY_ELIGIBILITY_RESULT.json", {"decision": "HOLD_SERVER_JSON_DRAFT_ONLY"})
    _write("public_launch/wave1/MCP_REGISTRY_SUBMISSION_RESULT.json", {"submission_performed": False})

    result = run_launch_wave1_report(write_result=True)

    assert result["github_release_created"] is True
    assert result["mcp_registry_eligibility_decision"] == "HOLD_SERVER_JSON_DRAFT_ONLY"
    assert Path("public_launch/wave1/LAUNCH_WAVE1_SUMMARY.md").exists()
