from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .feedback_reply_classifier import FeedbackReplyClassification
from .feedback_reply_packet import FeedbackReplyPacket


SelectedVertical = Literal["agentsec", "qira", "datacapsule", "portfolio", "hold_manual_triage", "block"]
RouteConfidence = Literal["low", "medium", "high"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class FeedbackReplyRoute(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_FeedbackReplyRoute/v0.1", alias="schema")
    route_id: str
    reply_id: str
    generated_at: str = Field(default_factory=timestamp)
    selected_vertical: SelectedVertical
    route_reason: str
    route_confidence: RouteConfidence = "medium"
    required_next_artifacts: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    can_create_memory_candidate: bool = False
    can_create_second_run_candidate: bool = False
    must_not_do: list[str] = Field(default_factory=list)


def route_feedback_reply(packet: FeedbackReplyPacket, classification: FeedbackReplyClassification) -> FeedbackReplyRoute:
    if classification.classification.startswith("BLOCK_"):
        return FeedbackReplyRoute(
            route_id=f"route-{packet.reply_id}",
            reply_id=packet.reply_id,
            selected_vertical="block",
            route_reason="blocked classification prevents vertical routing",
            route_confidence="high",
            blockers=[classification.classification],
            must_not_do=packet.must_not_do,
        )

    text = packet.reply_text_redacted.lower()
    selected: SelectedVertical
    reason: str
    confidence: RouteConfidence = "medium"
    if packet.related_vertical in {"agentsec", "qira", "datacapsule", "portfolio"}:
        selected = packet.related_vertical
        reason = "reply supplied an explicit related vertical"
        confidence = "high"
    elif any(term in text for term in ["tool", "manifest", "permission", "hidden instruction", "mcp"]):
        selected = "agentsec"
        reason = "tool, manifest, permission, or MCP feedback maps to AgentSec"
    elif any(term in text for term in ["patch", "ci", "diff", "code", "release"]):
        selected = "qira"
        reason = "patch, CI, diff, code, or release feedback maps to QIRA"
    elif any(term in text for term in ["dataset", "license", "privacy", "eval", "corpus"]):
        selected = "datacapsule"
        reason = "dataset, license, privacy, eval, or corpus feedback maps to DataCapsule"
    elif any(term in text for term in ["dashboard", "readout", "message", "portfolio"]):
        selected = "portfolio"
        reason = "dashboard, readout, messaging, or portfolio feedback maps to Portfolio"
    else:
        selected = "hold_manual_triage"
        reason = "reply is mixed or unclear"
        confidence = "low"

    return FeedbackReplyRoute(
        route_id=f"route-{packet.reply_id}",
        reply_id=packet.reply_id,
        selected_vertical=selected,
        route_reason=reason,
        route_confidence=confidence,
        required_next_artifacts=["redacted local artifact summary"] if classification.should_request_evidence else [],
        blockers=[] if selected != "hold_manual_triage" else ["manual_triage_needed"],
        can_create_memory_candidate=classification.classification in {
            "ACCEPT_FEEDBACK_MEMORY_CANDIDATE",
            "ACCEPT_SECOND_RUN_CANDIDATE",
        },
        can_create_second_run_candidate=classification.classification == "ACCEPT_SECOND_RUN_CANDIDATE",
        must_not_do=packet.must_not_do,
    )


def route_to_jsonable(route: FeedbackReplyRoute) -> dict[str, Any]:
    return route.model_dump(mode="json", by_alias=True)
