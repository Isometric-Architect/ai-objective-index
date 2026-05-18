from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import mcp_tools


DEFAULT_OUTPUT_PATH = Path("data/generated/release_readiness_v0_1.json")

CORE_COMMANDS = [
    "python -m pytest",
    "python -m ai_objective_index.mcp_smoke",
    "python -m ai_objective_index.datascope_qa",
    "python -m ai_objective_index.beta_readiness",
    "python -m ai_objective_index.openapi_export",
    "python -m ai_objective_index.mcp_manifest",
]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "docs/claim_boundaries.md",
    "docs/productization_mode.md",
    "docs/research_to_product_bridge.md",
    "docs/public_claim_policy.md",
    "api/openapi.json",
    "data/generated_mcp_tools_manifest.json",
    "reports/mcp_server_objective_index_v0_1.md",
    "reports/ai_tool_pricing_index_v0_1.md",
    "reports/source_trace_quality_report_v0_1.md",
    "hf_demo/app.py",
    "hf_dataset/README.md",
    "examples/python_client.py",
    "examples/claude_desktop_config_real_mcp_example.json",
]

GENERATED_OUTPUTS = [
    "data/generated/datascope_qa_results_v0_2.json",
    "data/generated/beta_readiness_report_v0_2.md",
    "data/generated/integrated_index_v0_2.json",
    "data/generated/integrated_source_traces_v0_2.json",
]

FORBIDDEN_ACTIONS = [
    "payment",
    "booking",
    "login",
    "email",
    "purchase",
    "contract",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _exists(path: str) -> bool:
    return (_repo_root() / path).exists()


def _read(path: str) -> str:
    full = _repo_root() / path
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


def _safety_boundary_check() -> dict[str, Any]:
    readme = _read("README.md").lower()
    claim_boundaries = _read("docs/claim_boundaries.md").lower()
    mcp_manifest = _read("data/generated_mcp_tools_manifest.json").lower()
    tools = set()
    try:
        manifest = json.loads(_read("data/generated_mcp_tools_manifest.json"))
        tools = {tool["name"] for tool in manifest.get("tools", [])}
    except Exception:
        manifest = {}

    forbidden_list_ok = all(action in (readme + claim_boundaries + mcp_manifest) for action in FORBIDDEN_ACTIONS)
    forbidden_as_tools = sorted(set(mcp_tools.FORBIDDEN_ACTIONS) & tools)
    no_publish_flag = "actual_publish_performed" not in readme or "actual_publish_performed: true" not in readme
    no_network_required = "no network" in readme or "no live crawling" in readme or "local-data-only" in readme
    return {
        "read_only_documented": "read-only" in readme or "read_only" in mcp_manifest,
        "forbidden_actions_documented": forbidden_list_ok,
        "forbidden_actions_exposed_as_tools": forbidden_as_tools,
        "no_automatic_publish_flag": no_publish_flag,
        "no_network_required_workflow_documented": no_network_required,
        "token": "BLOCK" if forbidden_as_tools else ("PASS" if forbidden_list_ok and no_publish_flag else "HOLD"),
    }


def _productization_boundary_check() -> dict[str, Any]:
    productization = _read("docs/productization_mode.md").lower()
    bridge = _read("docs/research_to_product_bridge.md").lower()
    public_claim = _read("docs/public_claim_policy.md").lower()
    combined = "\n".join([productization, bridge, public_claim])
    ceiling_ok = "not productization prohibition" in combined or "does not prohibit implementation" in combined
    evidence_ok = "product claims require product evidence" in combined
    return {
        "research_ceiling_not_productization_prohibition": ceiling_ok,
        "product_claims_require_product_evidence": evidence_ok,
        "token": "PASS" if ceiling_ok and evidence_ok else "HOLD",
    }


def run_release_readiness() -> dict[str, Any]:
    missing_files = [path for path in REQUIRED_FILES if not _exists(path)]
    missing_generated = [path for path in GENERATED_OUTPUTS if not _exists(path)]
    safety = _safety_boundary_check()
    productization = _productization_boundary_check()

    checks = {
        "core_commands_to_run_manually": [{"command": command, "token": "NOT_RUN"} for command in CORE_COMMANDS],
        "required_files": {
            "token": "PASS" if not missing_files else "HOLD",
            "checked": REQUIRED_FILES,
        },
        "generated_outputs": {
            "token": "PASS" if not missing_generated else "HOLD",
            "checked": GENERATED_OUTPUTS,
        },
        "safety_boundary": safety,
        "productization_boundary": productization,
    }

    warnings: list[str] = []
    if missing_files:
        warnings.append("Required release-prep files are missing.")
    if missing_generated:
        warnings.append("Generated readiness outputs are missing.")
    if safety["token"] != "PASS":
        warnings.append("Safety boundary needs review before public beta.")
    if productization["token"] != "PASS":
        warnings.append("Productization boundary needs review before public beta.")

    if safety["token"] == "BLOCK":
        overall = "BLOCK"
    elif missing_files or missing_generated or safety["token"] != "PASS" or productization["token"] != "PASS":
        overall = "HOLD"
    else:
        overall = "PASS"

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "checks": checks,
        "missing_files": missing_files,
        "missing_generated_outputs": missing_generated,
        "warnings": warnings,
        "recommended_next_action": "Review HOLD/BLOCK items before manual public beta release."
        if overall != "PASS"
        else "Manual release checklist may proceed; no publish was performed.",
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }


def save_release_readiness(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or run_release_readiness()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_release_readiness()
    path = save_release_readiness(results)
    print(f"Saved release readiness result: {path}")
    print(f"release_readiness={results['overall_token']}")
    print(f"actual_publish_performed={results['actual_publish_performed']}")


if __name__ == "__main__":
    main()
