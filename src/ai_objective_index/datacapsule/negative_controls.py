from __future__ import annotations

import re
from typing import Any

from .capsule_builder import build_datacapsule_from_metadata
from .models import DataCapsuleNegativeControl


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
