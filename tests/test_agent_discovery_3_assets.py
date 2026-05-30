from pathlib import Path

from ai_objective_index.agent_discovery_eval.agent_eval_report import write_eval_support_artifacts
from ai_objective_index.agent_discovery_eval.ordinary_agent_prompt_eval import run_ordinary_agent_prompt_eval


def test_agent_discovery_3_assets_exist():
    run_ordinary_agent_prompt_eval(write_result=True)
    write_eval_support_artifacts()

    required = [
        "agent_discovery_eval/ORDINARY_AGENT_EVAL_CASES.json",
        "agent_discovery_eval/ORDINARY_AGENT_NAIVE_BASELINE_RESULTS.json",
        "agent_discovery_eval/AOI_GUIDED_AGENT_RESULTS.json",
        "agent_discovery_eval/AGENT_PROMPT_EVAL_REPORT.json",
        "agent_discovery_eval/MANUAL_CHATGPT_CLAUDE_GEMINI_EVAL_SHEET.md",
        "examples/agent_prompts/eval/aoi_discover_prompt.md",
        "docs/aoi_public_discovery_smoke.md",
        "docs/aoi_ordinary_agent_prompt_evaluation.md",
    ]

    for path in required:
        assert Path(path).exists()


def test_manual_eval_sheet_warns_against_private_data_and_tokens():
    write_eval_support_artifacts()
    text = Path("agent_discovery_eval/MANUAL_CHATGPT_CLAUDE_GEMINI_EVAL_SHEET.md").read_text(encoding="utf-8")

    assert "do not upload private data" in text.lower()
    assert "tokens" in text.lower()
