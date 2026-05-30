from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .aoi_030a2_final_common import (
    FAILURE_RECOVERY_PATH,
    FINAL_BUILD_PATH,
    FINAL_MCP_GATE_PATH,
    FINAL_MCP_PUBLISH_PATH,
    FINAL_MCP_RECONCILE_PATH,
    FINAL_PREFLIGHT_PATH,
    FINAL_PYPI_UPLOAD_GATE_PATH,
    FINAL_PYPI_UPLOAD_PATH,
    FINAL_PYPI_VERIFY_PATH,
    FINAL_REPORT_PATH,
    NEXT_ACTIONS_PATH,
    TOKEN_SAFETY_NOTE_PATH,
    read_json,
    write_json,
    repo_root,
)
from .aoi_030a2_final_mcp_registry_gate import run_final_mcp_registry_gate
from .aoi_030a2_final_mcp_registry_publish import run_final_mcp_registry_publish
from .aoi_030a2_final_mcp_registry_reconcile import run_final_mcp_registry_reconcile
from .aoi_030a2_final_preflight import run_final_preflight
from .aoi_030a2_final_pypi_upload_gate import run_final_pypi_upload_gate
from .aoi_030a2_final_pypi_upload_runner import run_final_pypi_upload
from .aoi_030a2_final_pypi_verify import run_final_pypi_verify


def _decision(path: Path) -> str:
    return str(read_json(path).get("decision") or "MISSING")


def _ensure_outputs() -> None:
    if not read_json(FINAL_PREFLIGHT_PATH):
        run_final_preflight(write_result=True)
    if not read_json(FINAL_PYPI_UPLOAD_GATE_PATH):
        run_final_pypi_upload_gate(write_result=True)
    if not read_json(FINAL_PYPI_UPLOAD_PATH):
        run_final_pypi_upload(execute=False, write_result=True)
    if not read_json(FINAL_PYPI_VERIFY_PATH):
        run_final_pypi_verify(write_result=True)
    if not read_json(FINAL_MCP_GATE_PATH):
        run_final_mcp_registry_gate(write_result=True)
    if not read_json(FINAL_MCP_PUBLISH_PATH):
        run_final_mcp_registry_publish(execute=False, write_result=True)
    if not read_json(FINAL_MCP_RECONCILE_PATH):
        run_final_mcp_registry_reconcile(write_result=True)


def _write_text(path: Path, text: str) -> Path:
    destination = repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def build_final_report() -> str:
    _ensure_outputs()
    rows = [
        ("Final preflight", _decision(FINAL_PREFLIGHT_PATH)),
        ("Final build/twine", _decision(FINAL_BUILD_PATH)),
        ("PyPI upload gate", _decision(FINAL_PYPI_UPLOAD_GATE_PATH)),
        ("PyPI upload", _decision(FINAL_PYPI_UPLOAD_PATH)),
        ("PyPI verify", _decision(FINAL_PYPI_VERIFY_PATH)),
        ("MCP Registry gate", _decision(FINAL_MCP_GATE_PATH)),
        ("MCP Registry publish", _decision(FINAL_MCP_PUBLISH_PATH)),
        ("MCP Registry reconcile", _decision(FINAL_MCP_RECONCILE_PATH)),
    ]
    table = "\n".join(f"| {name} | `{decision}` |" for name, decision in rows)
    return f"""# AOI 0.3.0a2 Final Publish Report

This report summarizes the guarded final distribution path for `ai-objective-index==0.3.0a2`.

| Check | Decision |
| --- | --- |
{table}

## Included Agent Surfaces

- Agent-native capability card.
- Discover mode for source-traced candidate discovery.
- Preflight mode for route decisions, missing fields, claim ceilings, and ResidualOps escalation.
- Read-only REST endpoints for capability-card, discover, preflight, and adoption status.
- Read-only MCP tools for capability-card, discover, preflight, explanation, and examples.
- Package-data inclusion for agent discovery artifacts, agent schemas, prompt examples, and API examples.

## Token Safety

PyPI upload uses interactive `twine upload` only after `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES`. The runner does not accept tokens as command-line arguments, does not create `.pypirc`, does not store tokens, and records only redacted status metadata.

MCP Registry publish uses `mcp-publisher` only after PyPI verification and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`. Publisher output is redacted before it is written to result files.

## Not Claimed

- No security certification.
- No legal, privacy, license, or compliance clearance.
- No code-correctness proof.
- No quality guarantee.
- No product-readiness claim.
- No action authorization.
- No private ranking weights, thresholds, provider priors, anti-gaming details, private negative controls, private probe seeds, commercial routing policy, real feedback memory, or customer data.
"""


def write_supporting_notes() -> None:
    _write_text(
        TOKEN_SAFETY_NOTE_PATH,
        """# AOI 0.3.0a2 Token Safety Note

The final publish helpers require explicit environment confirmations before real upload or registry submission. PyPI credentials are entered only into the interactive `twine` prompt by the local operator. Tokens must not be pasted into chat, passed as command-line flags, committed, echoed, or stored in `.pypirc`.
""",
    )
    _write_text(
        FAILURE_RECOVERY_PATH,
        """# AOI 0.3.0a2 Failure Recovery

If PyPI reports that `0.3.0a2` already exists, do not overwrite, delete, or yank existing artifacts. Verify the existing package if possible, then choose a later version only after recording the conflict.

If MCP Registry publish reports authentication failure, rerun `mcp-publisher login github` locally and retry the publish runner with `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.

If registry search does not immediately show the entry after a publish success, treat it as propagation HOLD and retry reconcile later.
""",
    )
    _write_text(
        NEXT_ACTIONS_PATH,
        """# AOI 0.3.0a2 Next Actions

If PyPI upload and MCP Registry publish are complete, run AOI-AGENT-DISCOVERY-3 Public Discovery Smoke + Agent Prompt Evaluation.

If either distribution step is still HOLD because explicit confirmation was not present, rerun the gated command locally with the required environment variable and interactive authentication.
""",
    )


def run_final_publish_report(write_result: bool = True) -> dict[str, Any]:
    report = build_final_report()
    write_supporting_notes()
    if write_result:
        _write_text(FINAL_REPORT_PATH, report)
    result = {
        "schema": "AOI_030A2FinalPublishReportResult/v0.1",
        "decision": "PASS_FINAL_REPORT_WRITTEN",
        "report_path": str(FINAL_REPORT_PATH).replace("\\", "/"),
        "preflight_decision": _decision(FINAL_PREFLIGHT_PATH),
        "build_decision": _decision(FINAL_BUILD_PATH),
        "pypi_upload_decision": _decision(FINAL_PYPI_UPLOAD_PATH),
        "pypi_verify_decision": _decision(FINAL_PYPI_VERIFY_PATH),
        "mcp_registry_gate_decision": _decision(FINAL_MCP_GATE_PATH),
        "mcp_registry_publish_decision": _decision(FINAL_MCP_PUBLISH_PATH),
        "mcp_registry_reconcile_decision": _decision(FINAL_MCP_RECONCILE_PATH),
        "token_printed": False,
        "certification_claimed": False,
        "action_authorization_claimed": False,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_final_publish_report()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(
            "aoi_030a2_final_publish_report: "
            f"{result['decision']} report={result['report_path']}"
        )


if __name__ == "__main__":
    main()

