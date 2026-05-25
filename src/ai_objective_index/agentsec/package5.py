from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .fixture_corpus import OUTPUT_DIR, write_fixture_corpus
from .negative_controls import write_negative_control_result


PACKAGE_RESULT_PATH = OUTPUT_DIR / "AGENTSEC5_PACKAGE_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "AGENTSEC5_NEXT_STEPS.md"


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def build_agentsec5_package_result(corpus: dict[str, Any], negative_controls: dict[str, Any]) -> dict[str, Any]:
    if negative_controls["decision"].startswith("BLOCK"):
        decision = "BLOCK_AGENTSEC5_NEGATIVE_CONTROL_FALSE_PASS"
    else:
        decision = "PASS_AGENTSEC5_FIXTURE_CORPUS_AND_NEGATIVE_CONTROLS"
    return {
        "schema": "AgentSec5_PackageResult/v0.1",
        "generated_at": negative_controls["generated_at"],
        "decision": decision,
        "fixture_corpus_decision": corpus["decision"],
        "negative_control_decision": negative_controls["decision"],
        "fixture_count": corpus["fixture_count"],
        "false_pass_count": negative_controls["false_pass_count"],
        "mismatch_count": negative_controls["mismatch_count"],
        "actual_counts": negative_controls["actual_counts"],
        "known_limits": [
            "public-safe fake manifest fixtures only",
            "local negative controls only",
            "no live MCP call",
            "no external tool execution",
            "no URL fetch",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not action authorization",
        ],
        "must_not_claim": [
            "do not claim verified tool status",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim live gateway protection",
            "do not claim external action authorization",
            "do not claim legal compliance",
        ],
        "external_actions_performed": False,
        "network_used": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "token_printed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
    }


def write_next_steps(result: dict[str, Any]) -> Path:
    return _write_text(
        NEXT_STEPS_PATH,
        f"""# AgentSec-5 Next Steps

Decision: `{result['decision']}`

1. Keep adding public-safe fake fixtures for risky manifest patterns.
2. Keep exact private thresholds, provider priors, anti-gaming rules, and private negative-control banks outside the public repository.
3. Use false-pass count as a local regression signal only, not as security certification.
4. Consider AgentSec-6 for local manifest corpus ingestion from repository artifact folders.
""",
    )


def run_agentsec5_package() -> dict[str, Any]:
    corpus = write_fixture_corpus()
    negative_controls = write_negative_control_result()
    result = build_agentsec5_package_result(corpus, negative_controls)
    _write_json(PACKAGE_RESULT_PATH, result)
    write_next_steps(result)
    return result


def main() -> None:
    result = run_agentsec5_package()
    print(
        "agentsec5_package: "
        f"{result['decision']} fixtures={result['fixture_count']} false_passes={result['false_pass_count']}"
    )


if __name__ == "__main__":
    main()
