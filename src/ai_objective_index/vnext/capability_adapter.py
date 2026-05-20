from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from ai_objective_index.integrated_store import get_store_for_scope
from ai_objective_index.models import ActionObject, MissingField, SourceTrace
from ai_objective_index.scoring import score_object

from .capability_card import CapabilityCard
from .capability_trust import (
    CapabilityTrustCard,
    ObjectiveCapabilityMatch,
    compute_demo_trust_score,
)
from .evidence_summary import CapabilityEvidenceSummary, build_evidence_summary
from .objective_card import ObjectiveCard
from .risk_boundary import CapabilityRiskBoundary, assess_risk_boundary
from .route_decision import decide_route


def _value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def _integration_type(action_object: ActionObject) -> str:
    text = " ".join(
        [
            str(action_object.object_type),
            " ".join(action_object.categories),
            " ".join(action_object.capabilities),
        ]
    ).lower()
    if "mcp" in text:
        return "mcp_server"
    if "api" in text:
        return "api"
    if "dataset" in text:
        return "dataset"
    if "agent" in text:
        return "agent"
    if "package" in text or "python" in text:
        return "python_package"
    if "service" in text or "saas" in text:
        return "service"
    if "tool" in text:
        return "tool"
    return "unknown"


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def action_object_to_capability_card(action_object: ActionObject, traces: list[SourceTrace] | None = None) -> CapabilityCard:
    traces = traces or []
    return CapabilityCard(
        capability_id=f"capability:{action_object.object_id}",
        provider=action_object.provider if hasattr(action_object, "provider") else "unknown",
        name=action_object.name,
        version=getattr(action_object, "version", None),
        integration={
            "type": _integration_type(action_object),
            "object_type": _value(action_object.object_type),
            "official_url": action_object.official_url,
            "source_urls": action_object.source_urls,
        },
        supported_objectives=action_object.capabilities + action_object.categories,
        permission_scope=["read_only_metadata_candidate"],
        cost_model=action_object.pricing or {},
        latency_class="unknown",
        context_burden="unknown",
        evidence=[trace.model_dump(mode="json") for trace in traces],
        known_failures=[],
        allowed_use=["source-traced candidate comparison"],
        hold_use=["production use", "security-sensitive use", "purchase decision"],
        blocked_use=["payment", "booking", "login", "email sending", "purchase", "contract signing"],
        security={"status": "NOT_ASSESSED"},
        maintenance={"last_checked_at": str(action_object.last_checked_at) if action_object.last_checked_at else None},
    )


def source_traces_to_evidence_summary(
    action_object: ActionObject,
    traces: list[SourceTrace],
) -> CapabilityEvidenceSummary:
    return build_evidence_summary(action_object, traces)


def missing_fields_to_risk_boundary(
    action_object: ActionObject,
    missing_fields: list[MissingField],
) -> CapabilityRiskBoundary:
    return assess_risk_boundary(action_object, missing_fields)


def objective_request_to_objective_card(
    query: str,
    objective: str,
    domain: str = "mixed_ai_tools",
) -> ObjectiveCard:
    objective_id = _stable_id("objective", query, objective, domain)
    return ObjectiveCard(
        objective_id=objective_id,
        task=query,
        domain=domain,
        agent_role="ranking_agent",
        desired_output=objective,
        risk_level="medium",
        budget={},
        latency={},
        environment={"mode": "offline_local"},
        allowed_actions=["read-only ranking", "source trace review", "missing-field review"],
        forbidden_actions=["payment", "booking", "login", "email sending", "purchase", "contract signing"],
        evidence_requirement="source_trace_required",
        claim_ceiling="source-traced capability candidate; not verified",
    )


def _fit_ratio(score: float | int | None) -> float:
    if score is None:
        return 0.0
    return round(max(0.0, min(1.0, float(score) / 100.0)), 3)


def build_objective_capability_match(
    action_object: ActionObject,
    objective_card: ObjectiveCard,
    evidence_summary: CapabilityEvidenceSummary,
    risk_boundary: CapabilityRiskBoundary,
    missing_fields: list[str],
    score_components: dict[str, Any],
) -> ObjectiveCapabilityMatch:
    explanation: list[str] = []
    objective_fit = _fit_ratio(score_components.get("relevance"))
    integration = _integration_type(action_object)
    integration_fit = 0.8 if integration != "unknown" else 0.35
    policy_fit = 0.8 if evidence_summary.policy_found else 0.35
    evidence_fit = evidence_summary.confidence
    missing_penalty = min(1.0, len(missing_fields) / 10.0)
    forbidden_penalty = 1.0 if risk_boundary.forbidden_actions_detected else 0.0
    unsupported_penalty = 1.0 if risk_boundary.unsupported_claims_detected else 0.0
    explanation.append(f"Objective keyword fit is {objective_fit}.")
    explanation.append(f"Integration type inferred as {integration}.")
    if missing_fields:
        explanation.append(f"Missing fields reduce readiness: {', '.join(missing_fields[:6])}.")
    if risk_boundary.route_block_reasons:
        explanation.append("Hard boundary reasons are present; objective fit cannot override them.")
    return ObjectiveCapabilityMatch(
        objective_fit=objective_fit,
        domain_fit=0.75 if objective_card.domain in {"mixed_ai_tools", "ai_tools", "mcp_servers"} else 0.5,
        constraint_fit=0.65,
        integration_fit=integration_fit,
        policy_fit=policy_fit,
        evidence_fit=evidence_fit,
        missing_field_penalty=missing_penalty,
        forbidden_action_penalty=forbidden_penalty,
        unsupported_claim_penalty=unsupported_penalty,
        explanation=explanation,
    )


def build_capability_trust_card(
    action_object: ActionObject,
    objective_card: ObjectiveCard,
    traces: list[SourceTrace],
    query: str,
) -> CapabilityTrustCard:
    missing = get_store_for_scope("sample").list_missing_fields(action_object.object_id) if False else []
    # The store-specific missing field list is passed by callers when available.
    missing = missing
    score = score_object(action_object, query=query, objective=objective_card.desired_output, traces=traces)
    missing_names = list(score.missing_fields)
    evidence = build_evidence_summary(action_object, traces)
    boundary = assess_risk_boundary(
        action_object,
        [MissingField(field=name, why_it_matters="", recommended_source="", severity="medium") for name in missing_names],
    )
    match = build_objective_capability_match(
        action_object=action_object,
        objective_card=objective_card,
        evidence_summary=evidence,
        risk_boundary=boundary,
        missing_fields=missing_names,
        score_components=score.score_components,
    )
    route = decide_route(evidence, boundary, missing_names)
    score_components = {
        "objective_score": score.objective_score,
        "v0_2_score_components": score.score_components,
        "v0_2_penalties": score.penalties,
        "capability_trust": compute_demo_trust_score(match, evidence, boundary),
    }
    return CapabilityTrustCard(
        trust_card_id=_stable_id("trust", objective_card.objective_id, action_object.object_id),
        objective_id=objective_card.objective_id,
        capability_id=f"capability:{action_object.object_id}",
        object_id=action_object.object_id,
        name=action_object.name,
        provider=getattr(action_object, "provider", None),
        domain=objective_card.domain,
        integration_type=_integration_type(action_object),  # type: ignore[arg-type]
        status=str(_value(action_object.status)),
        source_trace_ids=[trace.trace_id for trace in traces],
        evidence_summary=evidence,
        match=match,
        risk_boundary=boundary,
        route_decision=route,
        score_components=score_components,
        residual_notes=[
            "CapabilityTrust is a routing readiness estimate, not verification.",
            "Security, quality, and product readiness are not asserted.",
        ],
        missing_fields=missing_names,
        known_limits=score.warnings + [
            "No live probes were executed.",
            "No gateway or security scanner was run.",
        ],
        generated_at=datetime.now(UTC).isoformat(),
    )


def search_capability_trust_cards(
    query: str,
    objective: str,
    domain: str = "mixed_ai_tools",
    data_scope: str = "sample",
    limit: int = 10,
) -> tuple[ObjectiveCard, list[CapabilityTrustCard], list[str]]:
    warnings: list[str] = []
    objective_card = objective_request_to_objective_card(query=query, objective=objective, domain=domain)
    try:
        store = get_store_for_scope(data_scope)
    except Exception as exc:  # pragma: no cover - defensive CLI path
        warnings.append(f"data_scope unavailable: {data_scope}: {exc}")
        return objective_card, [], warnings
    objects = store.search_objects(query=query, domain=domain, limit=limit)
    cards: list[CapabilityTrustCard] = []
    for action_object in objects:
        traces = store.get_traces(action_object.object_id)
        cards.append(build_capability_trust_card(action_object, objective_card, traces, query=query))
    return objective_card, cards, warnings
