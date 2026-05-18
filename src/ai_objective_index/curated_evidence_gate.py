from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from .models import ActionObject, SourceTrace


FORBIDDEN_ACTION_WORDS = {
    "automatically buys",
    "books appointments",
    "sends email",
    "logs in",
    "signs contracts",
    "payment execution",
    "purchase execution",
}


def _status(action_object: ActionObject) -> str:
    return str(action_object.status.value if hasattr(action_object.status, "value") else action_object.status).upper()


def _notes(action_object: ActionObject) -> str:
    return str(getattr(action_object, "notes", "") or "").lower()


def _valid_url(url: str | None) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _has_forbidden_action_claim(action_object: ActionObject) -> bool:
    text = " ".join(
        [
            action_object.name,
            action_object.summary,
            " ".join(action_object.capabilities),
            " ".join(action_object.categories),
            _notes(action_object),
        ]
    ).lower()
    return any(word in text for word in FORBIDDEN_ACTION_WORDS)


def evidence_gate_for_public_beta(
    action_object: ActionObject,
    traces: list[SourceTrace],
) -> dict[str, Any]:
    reasons: list[str] = []
    warnings: list[str] = []
    status = _status(action_object)

    if not _valid_url(action_object.official_url):
        return {
            "object_id": action_object.object_id,
            "token": "BLOCK_INVALID_URL",
            "public_beta_ready": False,
            "reasons": ["official_url is missing or not http/https"],
            "warnings": warnings,
        }
    if status in {"VERIFIED", "ACTION_READY"}:
        return {
            "object_id": action_object.object_id,
            "token": "BLOCK_VERIFIED_WITHOUT_VERIFICATION",
            "public_beta_ready": False,
            "reasons": ["Curated records cannot be VERIFIED or ACTION_READY without a future verification flow."],
            "warnings": warnings,
        }
    if _has_forbidden_action_claim(action_object):
        return {
            "object_id": action_object.object_id,
            "token": "BLOCK_FORBIDDEN_ACTION_CLAIM",
            "public_beta_ready": False,
            "reasons": ["Curated object contains forbidden action-claim language."],
            "warnings": warnings,
        }
    if not traces:
        return {
            "object_id": action_object.object_id,
            "token": "BLOCK_MISSING_SOURCE_TRACE",
            "public_beta_ready": False,
            "reasons": ["At least one source trace is required for public_beta."],
            "warnings": warnings,
        }
    if "placeholder" in _notes(action_object):
        return {
            "object_id": action_object.object_id,
            "token": "HOLD_PLACEHOLDER",
            "public_beta_ready": False,
            "reasons": ["Placeholder records are not public beta candidates."],
            "warnings": warnings,
        }
    if action_object.confidence < 0.5:
        return {
            "object_id": action_object.object_id,
            "token": "HOLD_LOW_CONFIDENCE",
            "public_beta_ready": False,
            "reasons": ["confidence is below 0.5"],
            "warnings": warnings,
        }
    if status not in {"EXTRACTED_UNVERIFIED", "UNVERIFIED", "CANDIDATE"}:
        warnings.append(f"Unexpected curated status: {status}")
    weak_traces = [trace.trace_id for trace in traces if trace.confidence < 0.5]
    if weak_traces:
        return {
            "object_id": action_object.object_id,
            "token": "HOLD_WEAK_SOURCE_TRACE",
            "public_beta_ready": False,
            "reasons": ["One or more source traces have confidence below 0.5."],
            "warnings": [*warnings, f"weak_traces={', '.join(weak_traces[:5])}"],
        }

    missing_nonfatal = list(action_object.missing_fields or [])
    return {
        "object_id": action_object.object_id,
        "token": "PASS_PUBLIC_BETA",
        "public_beta_ready": True,
        "reasons": ["Curated object passed public beta evidence gate."],
        "warnings": [*warnings, *[f"missing_field:{field}" for field in missing_nonfatal]],
    }
