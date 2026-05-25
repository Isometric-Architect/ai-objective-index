from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .capsule_builder import build_datacapsule_from_metadata
from .fixture_corpus import OUTPUT_DIR, PUBLIC_SAFE_FIXTURES, _bucket, _now
from .models import DataCapsuleNegativeControl

NEGATIVE_CONTROL_RESULT_PATH = OUTPUT_DIR / "DATACAPSULE5_NEGATIVE_CONTROL_RESULT.json"
NEGATIVE_CONTROL_REPORT_PATH = OUTPUT_DIR / "DATACAPSULE5_NEGATIVE_CONTROL_REPORT.md"


RISKY_REDACTIONS = [
    re.compile(r"\bprivacy\s+compliant\b", re.I),
    re.compile(r"\beval\s+clean\b", re.I),
    re.compile(r"\blegally\s+cleared\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\baction\s+authorized\b", re.I),
]


def _redact_finding(text: str) -> str:
    redacted = text
    for pattern in RISKY_REDACTIONS:
        redacted = pattern.sub("[redacted unsupported claim]", redacted)
    return redacted[:240]


def _control(control_id: str, goal: str, expected: str, actual: str, findings: list[str]) -> DataCapsuleNegativeControl:
    return DataCapsuleNegativeControl(
        control_id=control_id,
        control_goal=goal,
        expected_decision=expected,
        actual_decision=actual,
        result="PASS_NEGATIVE_CONTROL" if actual == expected else "FAIL_NEGATIVE_CONTROL",
        findings=[_redact_finding(item) for item in findings],
    )


def run_datacapsule_negative_controls() -> list[DataCapsuleNegativeControl]:
    unsupported_claim = build_datacapsule_from_metadata(
        {
            "data_id": "negative-control/unsupported-claim",
            "name": "Unsupported Claim Control",
            "source": "local-negative-control",
            "source_records": ["fixtures/claim.json"],
            "license": "MIT",
            "description": "This corpus is privacy compliant and eval clean.",
            "allowed_use": {"retrieve": True, "summarize": True},
        }
    )
    no_source = build_datacapsule_from_metadata(
        {
            "data_id": "negative-control/no-source",
            "name": "No Source Control",
            "license": "MIT",
            "allowed_use": {"retrieve": True},
        }
    )
    prompt_injection = build_datacapsule_from_metadata(
        {
            "data_id": "negative-control/prompt-injection",
            "name": "Prompt Injection Control",
            "source": "local-negative-control",
            "source_records": ["fixtures/prompt_injection.md"],
            "license": "MIT",
            "allowed_use": {"retrieve": True, "summarize": True},
            "risk_flags": {"prompt_injection": True},
        }
    )
    action_use = build_datacapsule_from_metadata(
        {
            "data_id": "negative-control/action-use",
            "name": "Action Use Control",
            "source": "local-negative-control",
            "source_records": ["fixtures/action.json"],
            "license": "MIT",
            "allowed_use": {"act": True},
        }
    )

    return [
        _control(
            "unsupported_claim_blocks",
            "Unsupported legal/privacy/eval-clean claims must block use decisions.",
            "BLOCK_UNSUPPORTED_CLAIM",
            unsupported_claim.use_permissions.retrieve.decision,
            unsupported_claim.residual_notes,
        ),
        _control(
            "no_source_holds",
            "Missing source records must not pass as source-reviewed data.",
            "HOLD_SOURCE_RIGHTS_REVIEW",
            no_source.use_permissions.retrieve.decision,
            no_source.residual_notes,
        ),
        _control(
            "prompt_injection_holds",
            "Prompt-injection risk in local metadata must hold retrieval use.",
            "HOLD_PROMPT_INJECTION_REVIEW",
            prompt_injection.use_permissions.retrieve.decision,
            prompt_injection.residual_notes,
        ),
        _control(
            "action_use_blocks",
            "DataCapsule metadata must never authorize external actions.",
            "BLOCK_ACTION_USE",
            action_use.use_permissions.act.decision,
            action_use.residual_notes,
        ),
    ]


def negative_control_summary(controls: list[DataCapsuleNegativeControl]) -> dict[str, Any]:
    false_passes = [item for item in controls if item.result != "PASS_NEGATIVE_CONTROL"]
    return {
        "control_count": len(controls),
        "pass_count": len(controls) - len(false_passes),
        "false_pass_count": len(false_passes),
        "failed_control_ids": [item.control_id for item in false_passes],
    }


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _is_false_pass(expected: str, actual: str) -> bool:
    return _bucket(expected) in {"hold", "block"} and _bucket(actual) == "allow"


def _is_downgrade_or_match(expected: str, actual: str) -> bool:
    order = {"allow": 0, "hold": 1, "block": 2}
    return order[_bucket(actual)] >= order[_bucket(expected)]


def run_datacapsule5_negative_controls(fixtures: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected = fixtures or PUBLIC_SAFE_FIXTURES
    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    false_passes: list[dict[str, Any]] = []
    actual_counts: Counter[str] = Counter()
    expected_counts: Counter[str] = Counter()

    for fixture in selected:
        expected = str(fixture["expected_decision"])
        primary_use = str(fixture["primary_use"])
        capsule = build_datacapsule_from_metadata(fixture["payload"], f"datacapsule5://{fixture['fixture_id']}")
        actual = getattr(capsule.use_permissions, primary_use).decision
        expected_counts[_bucket(expected)] += 1
        actual_counts[_bucket(actual)] += 1
        row = {
            "fixture_id": fixture["fixture_id"],
            "risk_theme": fixture["risk_theme"],
            "primary_use": primary_use,
            "expected_decision": expected,
            "actual_decision": actual,
            "expected_bucket": _bucket(expected),
            "actual_bucket": _bucket(actual),
            "passed": expected == actual or _is_downgrade_or_match(expected, actual),
            "false_pass": _is_false_pass(expected, actual),
            "capsule_id": capsule.capsule_id,
            "residual_note_count": len(capsule.residual_notes),
        }
        if not row["passed"]:
            mismatches.append(row)
        if row["false_pass"]:
            false_passes.append(row)
        rows.append(row)

    decision = (
        "PASS_DATACAPSULE5_NEGATIVE_CONTROLS"
        if not false_passes and not mismatches
        else "BLOCK_DATACAPSULE5_NEGATIVE_CONTROL_FALSE_PASS"
    )
    return {
        "schema": "DataCapsule5_NegativeControlResult/v0.1",
        "generated_at": _now(),
        "decision": decision,
        "fixture_count": len(rows),
        "expected_counts": {
            "allow": expected_counts["allow"],
            "hold": expected_counts["hold"],
            "block": expected_counts["block"],
        },
        "actual_counts": {
            "allow": actual_counts["allow"],
            "hold": actual_counts["hold"],
            "block": actual_counts["block"],
        },
        "false_pass_count": len(false_passes),
        "mismatch_count": len(mismatches),
        "false_passes": false_passes,
        "mismatches": mismatches,
        "results": rows,
        "public_safe": True,
        "contains_private_kernel": False,
        "contains_private_negative_control_seeds": False,
        "network_used": False,
        "crawler_used": False,
        "external_actions_performed": False,
        "token_printed": False,
        "can_certify_rights": False,
        "can_certify_privacy": False,
        "can_certify_quality": False,
        "can_prove_eval_cleanliness": False,
        "can_authorize_action": False,
        "known_limits": [
            "local fake fixture negative controls only",
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


def build_negative_control_markdown(result: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| `{item['fixture_id']}` | `{item['primary_use']}` | `{item['expected_decision']}` | `{item['actual_decision']}` | `{item['false_pass']}` |"
        for item in result["results"]
    )
    return f"""# DataCapsule-5 Negative Control Report

Decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Fixtures | `{result['fixture_count']}` |
| False pass count | `{result['false_pass_count']}` |
| Mismatch count | `{result['mismatch_count']}` |
| Network used | `False` |
| Crawler used | `False` |

| Fixture | Primary Use | Expected | Actual | False Pass |
| --- | --- | --- | --- | --- |
{rows}

## Boundary

Negative-control PASS only means these local fake data-use fixtures did not slip through this metadata capsule builder. It is not legal review, privacy certification, data-quality certification, evaluation-cleanliness proof, live source verification, or action authorization.
"""


def write_negative_control_result() -> dict[str, Any]:
    result = run_datacapsule5_negative_controls()
    _write_json(NEGATIVE_CONTROL_RESULT_PATH, result)
    _write_text(NEGATIVE_CONTROL_REPORT_PATH, build_negative_control_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run DataCapsule-5 public-safe negative controls.")
    parser.add_argument("--write-sample", action="store_true", help="Write public DataCapsule-5 negative-control outputs.")
    return parser


def main() -> None:
    build_parser().parse_args()
    result = write_negative_control_result()
    print(
        "datacapsule5_negative_controls: "
        f"{result['decision']} false_passes={result['false_pass_count']} mismatches={result['mismatch_count']}"
    )


if __name__ == "__main__":
    main()
