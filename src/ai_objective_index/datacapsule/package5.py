from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .fixture_corpus import OUTPUT_DIR, write_fixture_corpus
from .negative_controls import write_negative_control_result


PACKAGE_RESULT_PATH = OUTPUT_DIR / "DATACAPSULE5_PACKAGE_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "DATACAPSULE5_NEXT_STEPS.md"


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def build_datacapsule5_package_result(corpus: dict[str, Any], negative_controls: dict[str, Any]) -> dict[str, Any]:
    if negative_controls["decision"].startswith("BLOCK"):
        decision = "BLOCK_DATACAPSULE5_NEGATIVE_CONTROL_FALSE_PASS"
    else:
        decision = "PASS_DATACAPSULE5_FIXTURE_CORPUS_AND_NEGATIVE_CONTROLS"
    return {
        "schema": "DataCapsule5_PackageResult/v0.1",
        "generated_at": negative_controls["generated_at"],
        "decision": decision,
        "fixture_corpus_decision": corpus["decision"],
        "negative_control_decision": negative_controls["decision"],
        "fixture_count": corpus["fixture_count"],
        "false_pass_count": negative_controls["false_pass_count"],
        "mismatch_count": negative_controls["mismatch_count"],
        "actual_counts": negative_controls["actual_counts"],
        "known_limits": [
            "public-safe fake data-use fixtures only",
            "local negative controls only",
            "no crawling",
            "no live source verification",
            "no private data inspection",
            "not legal sufficiency",
            "not privacy compliance",
            "not data quality guarantee",
            "not evaluation cleanliness proof",
            "not action authorization",
        ],
        "must_not_claim": [
            "do not claim legal sufficiency",
            "do not claim privacy compliance",
            "do not claim data quality guarantee",
            "do not claim license clearance",
            "do not claim evaluation cleanliness",
            "do not claim action authorization",
            "do not claim purchasing advice",
        ],
        "external_actions_performed": False,
        "network_used": False,
        "crawler_used": False,
        "external_service_used": False,
        "token_printed": False,
        "can_certify_rights": False,
        "can_certify_privacy": False,
        "can_certify_quality": False,
        "can_prove_eval_cleanliness": False,
        "can_authorize_action": False,
    }


def write_next_steps(result: dict[str, Any]) -> Path:
    return _write_text(
        NEXT_STEPS_PATH,
        f"""# DataCapsule-5 Next Steps

Decision: `{result['decision']}`

1. Keep expanding public-safe fake fixtures for use-rights, privacy, source-trace, prompt-injection, eval-leak, and action-boundary cases.
2. Keep exact private scoring policy, receipt weighting, negative-control banks, and commercial data strategy outside the public repository.
3. Treat false-pass count as a local regression signal only, not as legal, privacy, quality, or eval-readiness proof.
4. Consider DataCapsule-6 for a repository-owned corpus audit bundle that can package capsule outputs for human review.
""",
    )


def run_datacapsule5_package() -> dict[str, Any]:
    corpus = write_fixture_corpus()
    negative_controls = write_negative_control_result()
    result = build_datacapsule5_package_result(corpus, negative_controls)
    _write_json(PACKAGE_RESULT_PATH, result)
    write_next_steps(result)
    return result


def main() -> None:
    result = run_datacapsule5_package()
    print(
        "datacapsule5_package: "
        f"{result['decision']} fixtures={result['fixture_count']} false_passes={result['false_pass_count']}"
    )


if __name__ == "__main__":
    main()
