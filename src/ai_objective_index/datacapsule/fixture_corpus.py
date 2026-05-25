from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json


OUTPUT_DIR = Path("public_launch") / "datacapsule5"
FIXTURE_CORPUS_PATH = OUTPUT_DIR / "DATACAPSULE5_FIXTURE_CORPUS.json"
FIXTURE_CORPUS_REPORT_PATH = OUTPUT_DIR / "DATACAPSULE5_FIXTURE_CORPUS_REPORT.md"


PUBLIC_SAFE_FIXTURES: list[dict[str, Any]] = [
    {
        "fixture_id": "safe-retrieval-public-docs",
        "primary_use": "retrieve",
        "expected_decision": "ALLOW_USE",
        "risk_theme": "source_traced_retrieval_metadata",
        "payload": {
            "data_id": "fixture.local/public-docs-corpus",
            "name": "Public docs corpus fixture",
            "source": "repository-local-fixture",
            "source_records": ["fixtures/public_docs_manifest.json"],
            "license": "MIT",
            "privacy_level": "public_metadata",
            "allowed_use": {"retrieve": True, "summarize": True},
            "risk_flags": {},
        },
    },
    {
        "fixture_id": "unknown-license-training",
        "primary_use": "train",
        "expected_decision": "HOLD_SOURCE_RIGHTS_REVIEW",
        "risk_theme": "rights_unknown",
        "payload": {
            "data_id": "fixture.local/unknown-license-training",
            "name": "Unknown license training fixture",
            "source": "repository-local-fixture",
            "source_records": ["fixtures/unknown_license_manifest.json"],
            "license": "unknown",
            "privacy_level": "public_metadata",
            "allowed_use": {"train": True},
            "risk_flags": {},
        },
    },
    {
        "fixture_id": "restricted-license-training",
        "primary_use": "train",
        "expected_decision": "BLOCK_LICENSE_RESTRICTED",
        "risk_theme": "restricted_license",
        "payload": {
            "data_id": "fixture.local/restricted-license-training",
            "name": "Restricted license training fixture",
            "source": "repository-local-fixture",
            "source_records": ["fixtures/restricted_license_manifest.json"],
            "license": "restricted internal use only",
            "privacy_level": "public_metadata",
            "allowed_use": {"train": True},
            "risk_flags": {},
        },
    },
    {
        "fixture_id": "privacy-risk-training",
        "primary_use": "train",
        "expected_decision": "BLOCK_PRIVACY_RISK",
        "risk_theme": "privacy_risk",
        "payload": {
            "data_id": "fixture.local/privacy-risk-training",
            "name": "Privacy risk training fixture",
            "source": "repository-local-fixture",
            "source_records": ["fixtures/privacy_risk_manifest.json"],
            "license": "MIT",
            "privacy_level": "personal_data_possible",
            "allowed_use": {"train": True, "share": True},
            "risk_flags": {"privacy": True},
        },
    },
    {
        "fixture_id": "prompt-injection-retrieval",
        "primary_use": "retrieve",
        "expected_decision": "HOLD_PROMPT_INJECTION_REVIEW",
        "risk_theme": "prompt_injection_review",
        "payload": {
            "data_id": "fixture.local/prompt-injection-retrieval",
            "name": "Prompt injection retrieval fixture",
            "source": "repository-local-fixture",
            "source_records": ["fixtures/prompt_injection_manifest.json"],
            "license": "MIT",
            "privacy_level": "public_metadata",
            "allowed_use": {"retrieve": True, "summarize": True},
            "risk_flags": {"prompt_injection": True},
        },
    },
    {
        "fixture_id": "eval-leak-evaluation",
        "primary_use": "evaluate",
        "expected_decision": "HOLD_EVAL_LEAK_REVIEW",
        "risk_theme": "eval_leak_review",
        "payload": {
            "data_id": "fixture.local/eval-leak-evaluation",
            "name": "Eval leak evaluation fixture",
            "source": "repository-local-fixture",
            "source_records": ["fixtures/eval_overlap_manifest.json"],
            "license": "MIT",
            "privacy_level": "public_metadata",
            "allowed_use": {"evaluate": True},
            "risk_flags": {"eval_leak": True},
        },
    },
    {
        "fixture_id": "unsupported-claim-metadata",
        "primary_use": "retrieve",
        "expected_decision": "BLOCK_UNSUPPORTED_CLAIM",
        "risk_theme": "unsupported_positive_claim",
        "payload": {
            "data_id": "fixture.local/unsupported-claim-metadata",
            "name": "Unsupported claim metadata fixture",
            "source": "repository-local-fixture",
            "source_records": ["fixtures/unsupported_claim_manifest.json"],
            "license": "MIT",
            "privacy_level": "public_metadata",
            "allowed_use": {"retrieve": True},
            "claims": {"privacy_compliant": True, "eval_clean": True},
        },
    },
    {
        "fixture_id": "missing-source-record",
        "primary_use": "retrieve",
        "expected_decision": "HOLD_SOURCE_RIGHTS_REVIEW",
        "risk_theme": "source_trace_missing",
        "payload": {
            "data_id": "fixture.local/missing-source-record",
            "name": "Missing source record fixture",
            "license": "MIT",
            "privacy_level": "public_metadata",
            "allowed_use": {"retrieve": True},
            "risk_flags": {},
        },
    },
    {
        "fixture_id": "action-use-request",
        "primary_use": "act",
        "expected_decision": "BLOCK_ACTION_USE",
        "risk_theme": "action_authorization_boundary",
        "payload": {
            "data_id": "fixture.local/action-use-request",
            "name": "Action use request fixture",
            "source": "repository-local-fixture",
            "source_records": ["fixtures/action_use_manifest.json"],
            "license": "MIT",
            "privacy_level": "public_metadata",
            "allowed_use": {"act": True},
            "risk_flags": {},
        },
    },
]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _bucket(decision: str) -> str:
    if decision.startswith("ALLOW"):
        return "allow"
    if decision.startswith("HOLD"):
        return "hold"
    if decision.startswith("BLOCK"):
        return "block"
    return "unknown"


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def build_fixture_corpus(fixtures: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected = fixtures or PUBLIC_SAFE_FIXTURES
    rows = []
    for fixture in selected:
        expected = str(fixture["expected_decision"])
        rows.append(
            {
                "fixture_id": fixture["fixture_id"],
                "risk_theme": fixture["risk_theme"],
                "primary_use": fixture["primary_use"],
                "expected_decision": expected,
                "expected_bucket": _bucket(expected),
                "payload": fixture["payload"],
            }
        )
    return {
        "schema": "DataCapsule5_FixtureCorpus/v0.1",
        "generated_at": _now(),
        "decision": "PASS_DATACAPSULE5_FIXTURE_CORPUS_READY",
        "fixture_count": len(rows),
        "fixtures": rows,
        "public_safe": True,
        "contains_real_private_data": False,
        "contains_private_kernel": False,
        "contains_private_negative_control_seeds": False,
        "network_used": False,
        "crawler_used": False,
        "external_actions_performed": False,
        "token_printed": False,
        "known_limits": [
            "public-safe fake data-use fixtures only",
            "local metadata checks only",
            "no crawling",
            "no live source verification",
            "not legal sufficiency",
            "not privacy compliance",
            "not data quality guarantee",
            "not evaluation cleanliness proof",
            "not action authorization",
        ],
    }


def build_fixture_corpus_markdown(corpus: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| `{item['fixture_id']}` | `{item['primary_use']}` | `{item['risk_theme']}` | `{item['expected_decision']}` |"
        for item in corpus["fixtures"]
    )
    return f"""# DataCapsule-5 Fixture Corpus

Decision: `{corpus['decision']}`

DataCapsule-5 adds public-safe fake data-use metadata fixtures for local negative-control testing.

| Fixture | Primary Use | Risk Theme | Expected Decision |
| --- | --- | --- | --- |
{rows}

## Boundary

The corpus contains fake local fixtures only. It does not include real private datasets, hidden rights analysis, private ranking weights, private thresholds, private negative-control seeds, legal review, privacy certification, data-quality certification, evaluation-cleanliness proof, or action authorization.
"""


def write_fixture_corpus() -> dict[str, Any]:
    corpus = build_fixture_corpus()
    _write_json(FIXTURE_CORPUS_PATH, corpus)
    _write_text(FIXTURE_CORPUS_REPORT_PATH, build_fixture_corpus_markdown(corpus))
    return corpus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write DataCapsule-5 public-safe use-rights fixture corpus.")
    parser.add_argument("--write-sample", action="store_true", help="Write public DataCapsule-5 fixture corpus outputs.")
    return parser


def main() -> None:
    build_parser().parse_args()
    corpus = write_fixture_corpus()
    print(f"datacapsule5_fixture_corpus: {corpus['decision']} fixtures={corpus['fixture_count']}")


if __name__ == "__main__":
    main()
