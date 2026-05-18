from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlparse

from ai_objective_index.models import ActionObject, SourceTrace


PASS_REGISTRY_CANDIDATE = "PASS_REGISTRY_CANDIDATE"
HOLD_MISSING_REPO = "HOLD_MISSING_REPO"
HOLD_MISSING_DOCS = "HOLD_MISSING_DOCS"
HOLD_WEAK_CAPABILITY = "HOLD_WEAK_CAPABILITY"
HOLD_FIXTURE_ONLY = "HOLD_FIXTURE_ONLY"
BLOCK_INVALID_URL = "BLOCK_INVALID_URL"
BLOCK_FORBIDDEN_STATUS = "BLOCK_FORBIDDEN_STATUS"
BLOCK_NO_TRACE = "BLOCK_NO_TRACE"

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


def _valid_url(url: str | None) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _docs(action_object: ActionObject) -> dict[str, Any]:
    return action_object.docs if isinstance(action_object.docs, dict) else {}


def _fixture_only(action_object: ActionObject) -> bool:
    return bool(getattr(action_object, "fixture_only", False))


def _has_forbidden_action_claim(action_object: ActionObject) -> bool:
    text = " ".join(
        [
            action_object.name,
            action_object.summary,
            " ".join(action_object.capabilities),
            " ".join(action_object.categories),
            str(getattr(action_object, "notes", "")),
        ]
    ).lower()
    return any(word in text for word in FORBIDDEN_ACTION_WORDS)


def validate_registry_object(
    action_object: ActionObject,
    traces: list[SourceTrace] | None = None,
) -> dict[str, Any]:
    traces = traces or []
    warnings: list[str] = []
    token = PASS_REGISTRY_CANDIDATE
    block = False
    docs = _docs(action_object)

    if not action_object.object_id or not action_object.name:
        token = BLOCK_NO_TRACE
        block = True
        warnings.append("object_id and name are required")
    if _status(action_object) in {"VERIFIED", "ACTION_READY"}:
        token = BLOCK_FORBIDDEN_STATUS
        block = True
        warnings.append("MCP registry intake cannot mark objects VERIFIED or ACTION_READY")
    if not traces and not block:
        token = BLOCK_NO_TRACE
        block = True
        warnings.append("At least one registry source trace is required")
    for url in [action_object.official_url, *action_object.source_urls]:
        if url and not _valid_url(url):
            token = BLOCK_INVALID_URL
            block = True
            warnings.append(f"invalid URL: {url}")
    if _has_forbidden_action_claim(action_object):
        token = "BLOCK_FORBIDDEN_ACTION_CLAIM"
        block = True
        warnings.append("forbidden action claim detected")
    if _fixture_only(action_object) and not block:
        token = HOLD_FIXTURE_ONLY
        warnings.append("fixture-only registry records are not public beta candidates")
    elif not (docs.get("repository_url") or docs.get("homepage_url")) and not block:
        token = HOLD_MISSING_REPO
        warnings.append("repository or homepage is missing")
    elif not docs.get("docs_url") and not block:
        token = HOLD_MISSING_DOCS
        warnings.append("documentation URL is missing")
    elif len(action_object.capabilities) <= 1 and not block:
        token = HOLD_WEAK_CAPABILITY
        warnings.append("capabilities are unclear")

    public_beta_ready = token == PASS_REGISTRY_CANDIDATE and not block
    return {
        "object_id": action_object.object_id,
        "token": token,
        "status": "BLOCK" if token.startswith("BLOCK") else ("PASS" if public_beta_ready else "HOLD"),
        "warnings": warnings,
        "trace_count": len(traces),
        "public_beta_ready": public_beta_ready,
    }


def evidence_gate_registry_public_beta(
    action_object: ActionObject,
    traces: list[SourceTrace] | None = None,
) -> dict[str, Any]:
    result = validate_registry_object(action_object, traces)
    if result["token"] == HOLD_FIXTURE_ONLY:
        result["public_beta_ready"] = False
    return result


def validate_registry_dataset(
    objects: list[ActionObject],
    traces: list[SourceTrace],
) -> dict[str, Any]:
    traces_by_object: dict[str, list[SourceTrace]] = {}
    for trace in traces:
        traces_by_object.setdefault(trace.object_id, []).append(trace)
    object_results = [
        validate_registry_object(action_object, traces_by_object.get(action_object.object_id, []))
        for action_object in objects
    ]
    counts = Counter(result["status"] for result in object_results)
    token_counts = Counter(result["token"] for result in object_results)
    return {
        "object_count": len(objects),
        "trace_count": len(traces),
        "pass_count": counts.get("PASS", 0),
        "hold_count": counts.get("HOLD", 0),
        "block_count": counts.get("BLOCK", 0),
        "token_counts": dict(token_counts),
        "warnings": [warning for result in object_results for warning in result.get("warnings", [])],
        "object_results": object_results,
        "public_beta_ready_count": sum(1 for result in object_results if result["public_beta_ready"]),
    }

