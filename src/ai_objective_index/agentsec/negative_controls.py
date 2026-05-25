from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .fixture_corpus import OUTPUT_DIR, PUBLIC_SAFE_FIXTURES, _bucket, _now
from .manifest_scanner import scan_manifest_payload
from .policy_gate import apply_policy_profile, developer_default_profile


NEGATIVE_CONTROL_RESULT_PATH = OUTPUT_DIR / "AGENTSEC5_NEGATIVE_CONTROL_RESULT.json"
NEGATIVE_CONTROL_REPORT_PATH = OUTPUT_DIR / "AGENTSEC5_NEGATIVE_CONTROL_REPORT.md"


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


def run_agentsec5_negative_controls(fixtures: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected = fixtures or PUBLIC_SAFE_FIXTURES
    profile = developer_default_profile()
    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    false_passes: list[dict[str, Any]] = []
    actual_counts: Counter[str] = Counter()
    expected_counts: Counter[str] = Counter()

    for fixture in selected:
        expected = str(fixture["expected_decision"])
        base_packet = scan_manifest_payload(fixture["payload"], f"agentsec5://{fixture['fixture_id']}")
        packet, hold_reasons, block_reasons = apply_policy_profile(base_packet, profile)
        actual = packet.risk_decision
        expected_counts[_bucket(expected)] += 1
        actual_counts[_bucket(actual)] += 1
        row = {
            "fixture_id": fixture["fixture_id"],
            "risk_theme": fixture["risk_theme"],
            "expected_decision": expected,
            "actual_decision": actual,
            "expected_bucket": _bucket(expected),
            "actual_bucket": _bucket(actual),
            "passed": expected == actual or _is_downgrade_or_match(expected, actual),
            "false_pass": _is_false_pass(expected, actual),
            "hold_reason_count": len(hold_reasons),
            "block_reason_count": len(block_reasons),
            "packet_id": packet.packet_id,
        }
        if not row["passed"]:
            mismatches.append(row)
        if row["false_pass"]:
            false_passes.append(row)
        rows.append(row)

    decision = (
        "PASS_AGENTSEC5_NEGATIVE_CONTROLS"
        if not false_passes and not mismatches
        else "BLOCK_AGENTSEC5_NEGATIVE_CONTROL_FALSE_PASS"
    )
    return {
        "schema": "AgentSec5_NegativeControlResult/v0.1",
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
        "profile_id": profile.profile_id,
        "public_safe": True,
        "contains_private_kernel": False,
        "network_used": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "external_actions_performed": False,
        "token_printed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
        "known_limits": [
            "local fake fixture negative controls only",
            "no live MCP call",
            "no external tool execution",
            "no URL fetch",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not action authorization",
        ],
    }


def build_negative_control_markdown(result: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| `{item['fixture_id']}` | `{item['expected_decision']}` | `{item['actual_decision']}` | `{item['false_pass']}` |"
        for item in result["results"]
    )
    return f"""# AgentSec-5 Negative Control Report

Decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Fixtures | `{result['fixture_count']}` |
| False pass count | `{result['false_pass_count']}` |
| Mismatch count | `{result['mismatch_count']}` |
| Profile | `{result['profile_id']}` |
| Live MCP calls | `False` |
| External tool execution | `False` |

| Fixture | Expected | Actual | False Pass |
| --- | --- | --- | --- |
{rows}

## Boundary

Negative-control PASS only means these local fake fixtures did not slip through this metadata scanner/profile. It is not verification, security certification, quality guarantee, product-readiness proof, live gateway protection, or action authorization.
"""


def write_negative_control_result() -> dict[str, Any]:
    result = run_agentsec5_negative_controls()
    _write_json(NEGATIVE_CONTROL_RESULT_PATH, result)
    _write_text(NEGATIVE_CONTROL_REPORT_PATH, build_negative_control_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AgentSec-5 public-safe negative controls.")
    parser.add_argument("--write-sample", action="store_true", help="Write public AgentSec-5 negative-control outputs.")
    return parser


def main() -> None:
    build_parser().parse_args()
    result = write_negative_control_result()
    print(
        "agentsec5_negative_controls: "
        f"{result['decision']} false_passes={result['false_pass_count']} mismatches={result['mismatch_count']}"
    )


if __name__ == "__main__":
    main()
