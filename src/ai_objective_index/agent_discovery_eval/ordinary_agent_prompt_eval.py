from __future__ import annotations

import argparse
import json
from typing import Any

from . import (
    AOI_GUIDED_RESULTS_PATH,
    EVAL_REPORT_PATH,
    NAIVE_BASELINE_PATH,
    SUMMARY_PATH,
    timestamp,
    write_json,
    write_text,
)
from .agent_eval_rubric import score_result, write_rubric
from .aoi_guided_agent_eval import aoi_guided_result_for_case
from .ordinary_agent_failure_fixtures import ordinary_agent_eval_cases, write_eval_cases


def naive_result_for_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "AOI_NaiveAgentBaselineResult/v0.1",
        "case_id": case["case_id"],
        "objective": case["objective"],
        "mode": "naive_tool_recommendation_fixture",
        "top_candidates": [{"candidate_id": "untraced-fast-answer", "name": "Fast Answer Tool"}],
        "source_traces": [],
        "missing_fields": [],
        "route_decision": "",
        "next_action": "",
        "must_not_claim": [],
        "residualops_escalation": "",
        "freshness": {},
        "tool_available_is_tool_authorized": True,
        "hallucinated_candidate_accepted": True,
        "external_action_authorized": "external action" in case["naive_agent_expected_failure"].lower(),
        "certification_or_readiness_claimed": "readiness" in case["naive_agent_expected_failure"].lower()
        or "verification" in case["naive_agent_expected_failure"].lower(),
        "expected_failure": case["naive_agent_expected_failure"],
    }


def run_ordinary_agent_prompt_eval(write_result: bool = True) -> dict[str, Any]:
    cases = ordinary_agent_eval_cases()
    naive_results: list[dict[str, Any]] = []
    guided_results: list[dict[str, Any]] = []
    for case in cases:
        naive = naive_result_for_case(case)
        guided = aoi_guided_result_for_case(case)
        naive.update(score_result(naive))
        guided.update(score_result(guided))
        naive_results.append(naive)
        guided_results.append(guided)

    naive_total = sum(item["score"] for item in naive_results)
    guided_total = sum(item["score"] for item in guided_results)
    max_total = sum(item["max_score"] for item in guided_results)
    report = {
        "schema": "AOI_AgentPromptEvalReport/v0.1",
        "generated_at": timestamp(),
        "case_count": len(cases),
        "method": "deterministic_offline_fixture_not_external_llm_eval",
        "naive_total_score": naive_total,
        "aoi_guided_total_score": guided_total,
        "max_total_score": max_total,
        "aoi_guided_improvement": guided_total - naive_total,
        "reduced_failure_modes": [
            "hallucinated candidate acceptance",
            "overclaim",
            "authorization confusion",
            "missing HOLD",
            "missing next_action",
            "missing ResidualOps escalation",
        ],
        "limits": [
            "Synthetic fixtures are not broad real-world agent adoption proof.",
            "No external LLM API was called.",
            "Scores should guide prompt and product iteration, not claim readiness.",
        ],
        "claim_boundary": [
            "not security certification",
            "not code correctness proof",
            "not legal, privacy, license, or compliance clearance",
            "not product readiness",
            "not action authorization",
        ],
    }

    if write_result:
        write_eval_cases()
        write_rubric()
        write_json(NAIVE_BASELINE_PATH, naive_results)
        write_json(AOI_GUIDED_RESULTS_PATH, guided_results)
        write_json(EVAL_REPORT_PATH, report)
        write_text(SUMMARY_PATH, summary_markdown(report))
    return report


def summary_markdown(report: dict[str, Any]) -> str:
    return f"""# AOI Agent Discovery 3 Summary

AOI Agent Discovery 3 creates a public discovery smoke and an offline ordinary-agent prompt evaluation pack.

- Cases: {report['case_count']}
- Naive fixture score: {report['naive_total_score']} / {report['max_total_score']}
- AOI-guided fixture score: {report['aoi_guided_total_score']} / {report['max_total_score']}
- Improvement: {report['aoi_guided_improvement']}

This is a deterministic offline fixture, not a live cross-model benchmark and not evidence of product readiness.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_ordinary_agent_prompt_eval(write_result=True)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            "ordinary_agent_prompt_eval: "
            f"cases={report['case_count']} improvement={report['aoi_guided_improvement']}"
        )


if __name__ == "__main__":
    main()
