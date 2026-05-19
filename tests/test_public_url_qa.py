from pathlib import Path

from ai_objective_index.public_url_qa import run_public_url_qa


def _not_checked(url):
    return {"checked": False, "reachable": False, "status": None, "error": "network unavailable"}


def _checked(url):
    return {"checked": True, "reachable": True, "status": 200, "error": None}


def test_public_url_qa_handles_network_unavailable():
    result = run_public_url_qa(url_checker=_not_checked, write_result=False)

    assert result["overall_token"] in {"NOT_CHECKED", "HOLD", "BLOCK"}
    assert result["github_public_checked"]["checked"] is False
    assert result["community_post_performed"] is False


def test_public_url_qa_passes_with_checked_urls():
    result = run_public_url_qa(url_checker=_checked, write_result=False)

    assert result["overall_token"] in {"PASS", "HOLD"}
    assert result["github_public_checked"]["reachable"] is True


def test_public_url_qa_detects_forbidden_claim_temp_file():
    path = Path("tests/__tmp_public_url_claim.md")
    path.write_text("These are the best MCP servers with guaranteed ranking.", encoding="utf-8")
    try:
        result = run_public_url_qa(url_checker=_checked, claim_files=[path], write_result=False)
    finally:
        path.unlink(missing_ok=True)

    assert result["overall_token"] == "BLOCK"
    assert result["forbidden_claim_findings"]
