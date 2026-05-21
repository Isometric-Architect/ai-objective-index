from __future__ import annotations

from typing import Any

from .probe_card import ProbeCard
from .probe_runner import run_probe_card


def run_negative_controls() -> dict[str, Any]:
    """Run deterministic local negative controls for the probe layer.

    The controls are fixture-only. They do not call live MCP servers, URLs,
    shell commands, external tools, or external LLMs.
    """
    unsupported_claim = ProbeCard(
        probe_type="negative_control",
        capability_id="capability:negative-control-unsupported-claim",
        data_scope="sample",
        probe_goal="Known-bad fixture must block unsupported quality/security claims.",
        canary_input={
            "name": "Fixture Tool",
            "summary": "This is a verified safe tool with security certified quality guaranteed output.",
        },
        negative_control_expected="BLOCK_UNSUPPORTED_CLAIM",
    )
    no_trigger = ProbeCard(
        probe_type="negative_control",
        capability_id="capability:negative-control-no-trigger",
        data_scope="sample",
        probe_goal="Known-bad fixture should fail if no unsupported claim appears.",
        canary_input={"name": "Fixture Tool", "summary": "Plain local metadata only."},
        negative_control_expected="FAIL_EXPECTED_NEGATIVE_CONTROL",
    )
    results = [run_probe_card(unsupported_claim), run_probe_card(no_trigger)]
    false_pass_count = sum(1 for result in results if result.result == "PASS_LOCAL")
    expected_blocks = sum(1 for result in results if result.result == "BLOCK_UNSUPPORTED_CLAIM")
    expected_failures = sum(1 for result in results if result.result == "FAIL_EXPECTED_NEGATIVE_CONTROL")
    return {
        "schema": "AOI_ProbeNegativeControlResult/v0.1",
        "negative_controls_run": len(results),
        "false_pass_count": false_pass_count,
        "expected_block_count": expected_blocks,
        "expected_failure_count": expected_failures,
        "overall_token": "PASS" if false_pass_count == 0 and expected_blocks >= 1 else "BLOCK",
        "results": [result.model_dump(mode="json", by_alias=True) for result in results],
        "network_used": False,
        "external_tool_execution": False,
        "gateway_execution": False,
        "token_printed": False,
    }


def main() -> None:
    result = run_negative_controls()
    print(
        "probe_negative_controls: "
        f"token={result['overall_token']} false_pass_count={result['false_pass_count']}"
    )


if __name__ == "__main__":
    main()
