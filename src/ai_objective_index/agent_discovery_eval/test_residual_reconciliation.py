from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import TEST_RESIDUAL_RECONCILIATION_PATH, repo_root, timestamp, write_json
from .external_model_feedback_schema import TEST_RESIDUAL_RECONCILIATION_SCHEMA


KNOWN_GENERATED_STATE_PATHS = [
    Path("data/registry"),
    Path("data/generated"),
    Path("hf_upload"),
    Path("aoi_test_tmp"),
]


def inspect_generated_state() -> list[str]:
    root = repo_root()
    present: list[str] = []
    for path in KNOWN_GENERATED_STATE_PATHS:
        full = root / path
        if full.exists():
            present.append(str(path).replace("\\", "/"))
    return present


def run_test_residual_reconciliation(write_result: bool = True) -> dict[str, object]:
    present_paths = inspect_generated_state()
    result = {
        "schema": TEST_RESIDUAL_RECONCILIATION_SCHEMA,
        "generated_at": timestamp(),
        "decision": "HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED",
        "classification": "unrelated_generated_payload_state",
        "package_regression": False,
        "stale_fixture": True,
        "needs_reprocess": True,
        "unsafe_to_fix_in_this_package": True,
        "safe_to_stage_generated_leftovers": False,
        "full_suite_green_claim_allowed": False,
        "known_failure_clusters": [
            "generated registry/datascope payload-state failures from the prior full-suite attempt",
            "registry intake payload guard recursion or stale generated state",
            "HF/generated bundle payload-state residuals outside the Discovery 4 package scope",
        ],
        "narrow_failure_slice": {
            "command": (
                "python -m pytest tests/test_api_mcp_registry_datascope.py tests/test_datascope_qa.py "
                "tests/test_mcp_registry_datascope.py tests/test_mcp_registry_eval.py "
                "tests/test_mcp_registry_export.py tests/test_mcp_registry_report_generator.py -q --tb=short"
            ),
            "failed_count": 9,
            "representative_failure": (
                "src/ai_objective_index/registry_intake/real_payload_guard.py "
                "is_fixture_payload recursion while exporting fixture MCP registry payload state"
            ),
            "affected_test_files": [
                "tests/test_api_mcp_registry_datascope.py",
                "tests/test_datascope_qa.py",
                "tests/test_mcp_registry_datascope.py",
                "tests/test_mcp_registry_eval.py",
                "tests/test_mcp_registry_export.py",
                "tests/test_mcp_registry_report_generator.py",
            ],
        },
        "inspected_generated_state_paths": present_paths,
        "narrow_safe_reprocess_candidate": "dedicated registry/datascope residual reconciliation package",
        "commands_not_run": [
            "destructive cleanup of generated state",
            "external registry fetch",
            "external LLM evaluation",
        ],
        "next_action": (
            "Do not claim global full-suite green until python -m pytest passes; "
            "handle generated registry/datascope payload-state in a separate reconciliation package."
        ),
        "claim_boundary": [
            "targeted package tests may pass while full-suite status remains HOLD",
            "classification is not proof that no regression exists",
            "no unrelated generated leftovers should be staged",
        ],
    }
    if write_result:
        write_json(TEST_RESIDUAL_RECONCILIATION_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_test_residual_reconciliation(write_result=True)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"test_residual_reconciliation: {result['decision']}")


if __name__ == "__main__":
    main()
