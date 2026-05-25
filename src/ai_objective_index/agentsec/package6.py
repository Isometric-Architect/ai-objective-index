from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .corpus_ingest import OUTPUT_DIR, write_agentsec6_sample_outputs


PACKAGE_RESULT_PATH = OUTPUT_DIR / "AGENTSEC6_PACKAGE_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "AGENTSEC6_NEXT_STEPS.md"


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def build_agentsec6_package_result(intake: dict[str, Any]) -> dict[str, Any]:
    if intake["decision"].startswith("BLOCK"):
        decision = "BLOCK_AGENTSEC6_CORPUS_INTAKE_FAILED"
    elif intake["decision"].startswith("HOLD"):
        decision = "HOLD_AGENTSEC6_CORPUS_REVIEW_REQUIRED"
    else:
        decision = "PASS_AGENTSEC6_LOCAL_MANIFEST_CORPUS_PACKAGE"
    return {
        "schema": "AgentSec6_PackageResult/v0.1",
        "generated_at": intake["generated_at"],
        "decision": decision,
        "corpus_intake_decision": intake["decision"],
        "policy_gate_decision": intake["policy_gate_decision"],
        "manifest_count": intake["manifest_count"],
        "allow_count": intake["allow_count"],
        "hold_count": intake["hold_count"],
        "block_count": intake["block_count"],
        "known_limits": [
            "repository-supplied manifest corpus only",
            "local metadata policy gate only",
            "no live MCP call",
            "no external tool execution",
            "no URL fetch",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not product-readiness proof",
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
        f"""# AgentSec-6 Next Steps

Decision: `{result['decision']}`

1. Keep using AgentSec-6 as a local manifest corpus ingestion artifact, not a live gateway.
2. Add a repository-owned manifest bundle format for developers to attach to issues or PRs.
3. Keep exact private thresholds, provider priors, anti-gaming rules, and private negative-control banks outside the public repository.
4. Consider AgentSec-7 for an optional local PR artifact bundle that summarizes manifest risk without posting comments or executing tools.
""",
    )


def run_agentsec6_package() -> dict[str, Any]:
    intake = write_agentsec6_sample_outputs()
    result = build_agentsec6_package_result(intake)
    _write_json(PACKAGE_RESULT_PATH, result)
    write_next_steps(result)
    return result


def main() -> None:
    result = run_agentsec6_package()
    print(
        "agentsec6_package: "
        f"{result['decision']} manifests={result['manifest_count']} "
        f"allow={result['allow_count']} hold={result['hold_count']} block={result['block_count']}"
    )


if __name__ == "__main__":
    main()
