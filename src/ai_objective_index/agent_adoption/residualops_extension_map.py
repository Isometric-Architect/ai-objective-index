from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from . import write_json, write_text


MAP_PATH = Path("agent_discovery") / "RESIDUALOPS_EXTENSION_MAP.md"


def build_residualops_extension_map() -> dict[str, Any]:
    return {
        "schema": "ResidualOps_ExtensionMap/v0.1",
        "aoi_role": "agent_and_developer_facing_public_discovery_router",
        "residualops_role": "enterprise_and_operator_facing_governance_layer",
        "routes": {
            "tool_manifest_risk": {
                "vertical": "AgentSec",
                "when_to_escalate": "tool, MCP, manifest, permissions, hidden instruction, namespace, or forbidden action risk",
            },
            "code_or_release_risk": {
                "vertical": "QIRA",
                "when_to_escalate": "patch, CI, diff, code review, release gate, merge, deploy, or package publish risk",
            },
            "data_or_use_boundary_risk": {
                "vertical": "DataCapsule",
                "when_to_escalate": "dataset, corpus, source rights, privacy, license, eval leakage, retention, or act-use risk",
            },
            "enterprise_receipt_tracking": {
                "vertical": "ResidualOps dashboard",
                "when_to_escalate": "portfolio-level receipt tracking, feedback memory, reviewer readout, or share-pack status",
            },
        },
        "claim_boundary": [
            "AOI is a public source-traced discovery and pre-use routing layer.",
            "ResidualOps adds local/offline enterprise review artifacts and receipt memory.",
            "ResidualOps results are not security certification, product readiness, legal clearance, privacy audit, license clearance, or action authorization without separate evidence.",
        ],
        "private_kernel_not_disclosed": True,
    }


def route_for_issue(issue_text: str) -> str:
    lowered = issue_text.lower()
    if any(token in lowered for token in ["tool", "manifest", "permission", "hidden instruction", "mcp"]):
        return "AgentSec"
    if any(token in lowered for token in ["code", "patch", "diff", "ci", "release", "merge", "deploy"]):
        return "QIRA"
    if any(token in lowered for token in ["data", "dataset", "corpus", "license", "privacy", "eval"]):
        return "DataCapsule"
    return "ResidualOps dashboard"


def extension_map_markdown(payload: dict[str, Any] | None = None) -> str:
    payload = payload or build_residualops_extension_map()
    rows = []
    for key, route in payload["routes"].items():
        rows.append(f"| `{key}` | {route['vertical']} | {route['when_to_escalate']} |")
    return """# ResidualOps Extension Map

AOI is the agent/developer-facing public discovery and pre-use trust router. ResidualOps is the enterprise/operator-facing governance layer for deeper local receipt workflows.

| Risk area | Route | Escalate when |
| --- | --- | --- |
""" + "\n".join(rows) + """

No ResidualOps result is security certification, code correctness proof, legal/privacy/license/eval-clean clearance, quality guarantee, product readiness, or external action authorization unless separate evidence and authorization exist.

Private ranking weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, commercial routing policy, real feedback memory, and customer-specific data remain private.
"""


def write_extension_map() -> dict[str, Any]:
    payload = build_residualops_extension_map()
    write_json(Path("schemas") / "agent" / "residualops_extension_map.example.json", payload)
    write_text(MAP_PATH, extension_map_markdown(payload))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = write_extension_map() if args.write else build_residualops_extension_map()
    print(f"residualops_extension_map: routes={len(payload['routes'])}")


if __name__ == "__main__":
    main()

