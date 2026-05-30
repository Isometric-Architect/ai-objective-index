from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


OUTREACH_DIR = Path("pilot_outreach")
PERSONAS_PATH = OUTREACH_DIR / "PILOT_DISCOVERY_PERSONAS.json"


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def build_discovery_personas() -> list[dict[str, Any]]:
    must_not_claim = [
        "security certification",
        "code correctness proof",
        "legal/privacy/license clearance",
        "eval-clean proof",
        "product readiness",
        "quality guarantee",
        "external action authorization",
    ]
    return [
        {
            "schema": "ResidualOps_PilotDiscoveryPersona/v0.1",
            "persona_id": "mcp-tool-maintainer",
            "label": "MCP/tool maintainer",
            "likely_interest": "agent_security",
            "suggested_vertical": "agentsec",
            "what_to_show": "AgentSec manifest receipt, HOLD/BLOCK examples, and claim ceiling.",
            "what_to_ask": "Which manifest fields or permission-scope warnings would make the review more useful?",
            "must_not_claim": must_not_claim,
            "manual_only": True,
        },
        {
            "schema": "ResidualOps_PilotDiscoveryPersona/v0.1",
            "persona_id": "ai-coding-workflow-builder",
            "label": "AI coding workflow builder",
            "likely_interest": "ai_code_review",
            "suggested_vertical": "qira",
            "what_to_show": "QIRA task packet, behavior contract, release-gate receipt, and second-run delta.",
            "what_to_ask": "Which missing CI or reviewer evidence should keep a patch on HOLD?",
            "must_not_claim": must_not_claim,
            "manual_only": True,
        },
        {
            "schema": "ResidualOps_PilotDiscoveryPersona/v0.1",
            "persona_id": "data-steward",
            "label": "Data steward",
            "likely_interest": "data_governance",
            "suggested_vertical": "datacapsule",
            "what_to_show": "DataCapsule manifest-only receipt, use-boundary table, and known limits.",
            "what_to_ask": "Which source, rights, privacy, or eval-overlap fields are missing?",
            "must_not_claim": must_not_claim,
            "manual_only": True,
        },
        {
            "schema": "ResidualOps_PilotDiscoveryPersona/v0.1",
            "persona_id": "founder-operator",
            "label": "Founder/operator",
            "likely_interest": "founder_operator",
            "suggested_vertical": "portfolio",
            "what_to_show": "Unified portfolio dashboard and external-safe share pack.",
            "what_to_ask": "Is the workflow understandable enough for a bounded customer-discovery conversation?",
            "must_not_claim": must_not_claim,
            "manual_only": True,
        },
        {
            "schema": "ResidualOps_PilotDiscoveryPersona/v0.1",
            "persona_id": "developer-tool-researcher",
            "label": "Developer tool researcher",
            "likely_interest": "developer_tools",
            "suggested_vertical": "portfolio",
            "what_to_show": "Packet -> check/probe -> receipt -> ALLOW/HOLD/BLOCK -> feedback memory.",
            "what_to_ask": "Which parts look like reusable developer-tool primitives, and which remain unclear?",
            "must_not_claim": must_not_claim,
            "manual_only": True,
        },
        {
            "schema": "ResidualOps_PilotDiscoveryPersona/v0.1",
            "persona_id": "ai-governance-reviewer",
            "label": "AI governance reviewer",
            "likely_interest": "ai_safety_governance",
            "suggested_vertical": "portfolio",
            "what_to_show": "Claim-boundary sheets, do-not-send guard, and feedback triage taxonomy.",
            "what_to_ask": "Which claim boundaries should be clearer before any broader distribution?",
            "must_not_claim": must_not_claim,
            "manual_only": True,
        },
        {
            "schema": "ResidualOps_PilotDiscoveryPersona/v0.1",
            "persona_id": "security-minded-engineer",
            "label": "Security-minded engineer",
            "likely_interest": "agent_security",
            "suggested_vertical": "agentsec",
            "what_to_show": "AgentSec and QIRA HOLD/BLOCK examples plus no-live-execution limits.",
            "what_to_ask": "Which negative controls or review questions should be added before a real local pilot?",
            "must_not_claim": must_not_claim,
            "manual_only": True,
        },
    ]


def write_personas(path: Path = PERSONAS_PATH) -> dict[str, Any]:
    payload = {
        "schema": "ResidualOps_PilotDiscoveryPersonas/v0.1",
        "generated_at": timestamp(),
        "persona_count": len(build_discovery_personas()),
        "personas": build_discovery_personas(),
        "manual_only": True,
        "auto_contact_performed": False,
        "external_api_used": False,
    }
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    result = write_personas()
    print(f"pilot_discovery_personas: personas={result['persona_count']} manual_only={result['manual_only']}")


if __name__ == "__main__":
    main()
