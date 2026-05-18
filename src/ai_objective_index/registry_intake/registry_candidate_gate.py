from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from ai_objective_index.models import ActionObject, SourceTrace


PASS_PUBLIC_BETA_CANDIDATE = "PASS_PUBLIC_BETA_CANDIDATE"
HOLD_FIXTURE_ONLY = "HOLD_FIXTURE_ONLY"
HOLD_MISSING_DESCRIPTION = "HOLD_MISSING_DESCRIPTION"
HOLD_MISSING_REPOSITORY = "HOLD_MISSING_REPOSITORY"
HOLD_MISSING_PACKAGE = "HOLD_MISSING_PACKAGE"
HOLD_WEAK_TRACE = "HOLD_WEAK_TRACE"
BLOCK_INVALID_URL = "BLOCK_INVALID_URL"
BLOCK_FORBIDDEN_STATUS = "BLOCK_FORBIDDEN_STATUS"
BLOCK_NO_TRACE = "BLOCK_NO_TRACE"
BLOCK_SECURITY_CERTIFICATION_CLAIM = "BLOCK_SECURITY_CERTIFICATION_CLAIM"

NOT_ASSERTED = [
    "security_certification",
    "supplier_verification",
    "quality_guarantee",
    "action_permission",
    "purchasing_advice",
]

SECURITY_CERTIFICATION_PHRASES = {
    "security certified",
    "security certification",
    "certified safe",
    "safety certified",
    "guaranteed secure",
    "verified secure",
}


def _status(action_object: ActionObject) -> str:
    status = action_object.status
    return str(status.value if hasattr(status, "value") else status).upper()


def _valid_url(url: str | None) -> bool:
    if not url:
        return True
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _docs(action_object: ActionObject) -> dict[str, Any]:
    return action_object.docs if isinstance(action_object.docs, dict) else {}


def _has_repository(action_object: ActionObject) -> bool:
    docs = _docs(action_object)
    return bool(docs.get("repository_url") or docs.get("github_url"))


def _has_package_or_install(action_object: ActionObject) -> bool:
    return bool(
        getattr(action_object, "package_metadata", None)
        or getattr(action_object, "integration_methods", None)
        or getattr(action_object, "remote_metadata", None)
    )


def _has_homepage(action_object: ActionObject) -> bool:
    docs = _docs(action_object)
    return bool(docs.get("homepage_url") or action_object.official_url)


def _has_registry_metadata(action_object: ActionObject) -> bool:
    return _has_repository(action_object) or _has_package_or_install(action_object) or _has_homepage(action_object)


def _security_certification_claim(action_object: ActionObject) -> bool:
    text = " ".join(
        [
            action_object.name,
            action_object.summary,
            " ".join(action_object.capabilities),
            " ".join(action_object.categories),
            str(getattr(action_object, "notes", "")),
        ]
    ).lower()
    return any(phrase in text for phrase in SECURITY_CERTIFICATION_PHRASES)


def _trace_strength(traces: list[SourceTrace]) -> float:
    if not traces:
        return 0.0
    return sum(float(trace.confidence) for trace in traces) / len(traces)


def _source_is_fixture(action_object: ActionObject, source_mode: str) -> bool:
    return source_mode.lower() in {"fixture", "fixture_only"} or bool(getattr(action_object, "fixture_only", False))


def evaluate_registry_beta_candidate(
    obj: ActionObject | dict[str, Any],
    traces: list[SourceTrace] | None,
    source_mode: str = "live_or_manual_raw",
) -> dict[str, Any]:
    """Evaluate a registry record for beta-candidate display.

    Passing this gate means only that the record is useful enough for a public
    beta MCP metadata scope. It never means the server is verified, safe, high
    quality, or action-ready.
    """

    action_object = obj if isinstance(obj, ActionObject) else ActionObject.model_validate(obj)
    traces = traces or []
    warnings: list[str] = []
    holds: list[str] = []
    blocks: list[str] = []

    if not action_object.object_id or not action_object.name:
        blocks.append(BLOCK_NO_TRACE)
        warnings.append("object_id and name are required")

    if _status(action_object) in {"VERIFIED", "ACTION_READY"}:
        blocks.append(BLOCK_FORBIDDEN_STATUS)
        warnings.append("Registry metadata candidates cannot be VERIFIED or ACTION_READY.")

    if not traces:
        blocks.append(BLOCK_NO_TRACE)
        warnings.append("At least one source trace is required.")

    for url in [action_object.official_url, *action_object.source_urls]:
        if not _valid_url(url):
            blocks.append(BLOCK_INVALID_URL)
            warnings.append(f"Invalid URL: {url}")

    docs = _docs(action_object)
    for url in [docs.get("docs_url"), docs.get("repository_url"), docs.get("homepage_url"), docs.get("registry_url")]:
        if not _valid_url(url):
            blocks.append(BLOCK_INVALID_URL)
            warnings.append(f"Invalid URL: {url}")

    if _security_certification_claim(action_object):
        blocks.append(BLOCK_SECURITY_CERTIFICATION_CLAIM)
        warnings.append("Security certification claim detected; AOI cannot promote that claim.")

    if _source_is_fixture(action_object, source_mode):
        holds.append(HOLD_FIXTURE_ONLY)
        warnings.append("Fixture-only records are not public beta MCP candidates.")

    if not action_object.summary or action_object.summary.strip().lower() in {"mcp registry server metadata record.", "unknown"}:
        holds.append(HOLD_MISSING_DESCRIPTION)
        warnings.append("Description is missing or too generic.")

    if not _has_repository(action_object):
        holds.append(HOLD_MISSING_REPOSITORY)
        warnings.append("Repository metadata is missing.")

    if not _has_package_or_install(action_object):
        holds.append(HOLD_MISSING_PACKAGE)
        warnings.append("Package, remote, or install metadata is missing.")

    if _trace_strength(traces) < 0.4:
        holds.append(HOLD_WEAK_TRACE)
        warnings.append("Source trace confidence is weak.")

    confidence = float(action_object.confidence or 0)
    has_minimum_metadata = bool(action_object.summary) or _has_registry_metadata(action_object)
    beta_candidate = (
        not blocks
        and HOLD_FIXTURE_ONLY not in holds
        and has_minimum_metadata
        and confidence >= 0.4
        and _status(action_object) == "EXTRACTED_UNVERIFIED"
    )
    decision = PASS_PUBLIC_BETA_CANDIDATE if beta_candidate else (blocks[0] if blocks else (holds[0] if holds else HOLD_WEAK_TRACE))

    return {
        "object_id": action_object.object_id,
        "decision": decision,
        "holds": holds,
        "blocks": blocks,
        "beta_candidate": beta_candidate,
        "verified": False,
        "action_ready": False,
        "status_to_display": "REGISTRY_METADATA_CANDIDATE" if beta_candidate else "EXTRACTED_UNVERIFIED",
        "warnings": warnings,
        "not_asserted": NOT_ASSERTED,
        "trace_count": len(traces),
        "confidence": confidence,
        "source_mode": source_mode,
    }
