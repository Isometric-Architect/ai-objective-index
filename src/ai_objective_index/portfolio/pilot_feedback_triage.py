from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_discovery_personas import OUTREACH_DIR, timestamp


TRIAGE_TAXONOMY_PATH = OUTREACH_DIR / "PILOT_FEEDBACK_TRIAGE_TAXONOMY.json"


TRIAGE_CATEGORIES: list[dict[str, Any]] = [
    {
        "category": "confusing_claim",
        "severity_default": "medium",
        "recommended_next_action": "rewrite claim boundary or add known-limit note",
        "route_to": "portfolio",
        "second_run_needed": False,
        "owner_consent_needed": False,
    },
    {
        "category": "missing_evidence",
        "severity_default": "medium",
        "recommended_next_action": "request redacted local evidence reference",
        "route_to": "portfolio",
        "second_run_needed": True,
        "owner_consent_needed": True,
    },
    {
        "category": "wrong_allow_hold_block",
        "severity_default": "high",
        "recommended_next_action": "classify feedback and schedule local second-run if consented",
        "route_to": "portfolio",
        "second_run_needed": True,
        "owner_consent_needed": True,
    },
    {
        "category": "unclear_dashboard",
        "severity_default": "low",
        "recommended_next_action": "update dashboard label or operator script",
        "route_to": "portfolio",
        "second_run_needed": False,
        "owner_consent_needed": False,
    },
    {
        "category": "bad_operator_script",
        "severity_default": "medium",
        "recommended_next_action": "revise manual walkthrough wording",
        "route_to": "portfolio",
        "second_run_needed": False,
        "owner_consent_needed": False,
    },
    {
        "category": "missing_vertical",
        "severity_default": "medium",
        "recommended_next_action": "add vertical candidate to portfolio backlog",
        "route_to": "portfolio",
        "second_run_needed": False,
        "owner_consent_needed": False,
    },
    {
        "category": "privacy_or_license_concern",
        "severity_default": "high",
        "recommended_next_action": "route to DataCapsule and keep claim ceiling explicit",
        "route_to": "datacapsule",
        "second_run_needed": True,
        "owner_consent_needed": True,
    },
    {
        "category": "security_claim_concern",
        "severity_default": "high",
        "recommended_next_action": "route to AgentSec and claim-boundary review",
        "route_to": "agentsec",
        "second_run_needed": True,
        "owner_consent_needed": True,
    },
    {
        "category": "data_boundary_concern",
        "severity_default": "high",
        "recommended_next_action": "route to DataCapsule use-boundary review",
        "route_to": "datacapsule",
        "second_run_needed": True,
        "owner_consent_needed": True,
    },
    {
        "category": "code_release_boundary_concern",
        "severity_default": "high",
        "recommended_next_action": "route to QIRA behavior-contract review",
        "route_to": "qira",
        "second_run_needed": True,
        "owner_consent_needed": True,
    },
    {
        "category": "tool_manifest_boundary_concern",
        "severity_default": "high",
        "recommended_next_action": "route to AgentSec manifest review",
        "route_to": "agentsec",
        "second_run_needed": True,
        "owner_consent_needed": True,
    },
    {
        "category": "private_kernel_concern",
        "severity_default": "critical",
        "recommended_next_action": "block publication and review public/private split",
        "route_to": "portfolio",
        "second_run_needed": False,
        "owner_consent_needed": False,
    },
    {
        "category": "request_real_pilot",
        "severity_default": "medium",
        "recommended_next_action": "use ROE-12 owner-consented local intake before any pilot",
        "route_to": "portfolio",
        "second_run_needed": True,
        "owner_consent_needed": True,
    },
    {
        "category": "other",
        "severity_default": "unknown",
        "recommended_next_action": "manual triage",
        "route_to": "portfolio",
        "second_run_needed": False,
        "owner_consent_needed": False,
    },
]


def route_feedback_category(category: str) -> dict[str, Any]:
    for item in TRIAGE_CATEGORIES:
        if item["category"] == category:
            return item
    return TRIAGE_CATEGORIES[-1]


def write_feedback_triage_taxonomy(path: Path = TRIAGE_TAXONOMY_PATH) -> dict[str, Any]:
    payload = {
        "schema": "ResidualOps_PilotFeedbackTriage/v0.1",
        "generated_at": timestamp(),
        "category_count": len(TRIAGE_CATEGORIES),
        "categories": TRIAGE_CATEGORIES,
        "auto_issue_creation_performed": False,
        "external_api_used": False,
    }
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
