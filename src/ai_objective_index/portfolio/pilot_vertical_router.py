from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .pilot_intake_packet import PilotIntakePacket, default_forbidden_actions, pilot_must_not_claim


SelectedVertical = Literal[
    "agentsec",
    "qira",
    "datacapsule",
    "hold_manual_triage",
    "block_insufficient_consent",
    "block_forbidden_artifact",
]
RouteConfidence = Literal["low", "medium", "high"]

AGENTSEC_ARTIFACTS = {"mcp_manifest", "tool_manifest"}
QIRA_ARTIFACTS = {"pr_diff", "patch_text", "ci_summary"}
DATACAPSULE_ARTIFACTS = {"dataset_manifest", "corpus_manifest", "dataset_card"}


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class PilotVerticalRoute(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotVerticalRoute/v0.1", alias="schema")
    route_id: str
    intake_id: str
    generated_at: str = Field(default_factory=timestamp)
    selected_vertical: SelectedVertical
    route_reason: str
    route_confidence: RouteConfidence = "low"
    required_next_artifacts: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    claim_ceiling: str = "local/offline owner-consented pilot intake route only"
    can_generate_pilot_receipt: bool = False
    must_not_do: list[str] = Field(default_factory=default_forbidden_actions)
    must_not_claim: list[str] = Field(default_factory=pilot_must_not_claim)


def _has_forbidden_scope(packet: PilotIntakePacket) -> bool:
    scope = packet.allowed_review_scope
    return any(
        [
            scope.external_network,
            scope.github_api_call,
            scope.live_tool_execution,
            scope.external_repo_mutation,
            scope.posting_or_commenting,
            packet.external_action_requested,
        ]
    )


def route_intake_packet(packet: PilotIntakePacket) -> PilotVerticalRoute:
    artifact_type = packet.provided_artifact.artifact_type
    consent_status = packet.owner_consent.status
    blockers: list[str] = []

    if consent_status in {"unknown"}:
        return PilotVerticalRoute(
            route_id=f"route-{packet.intake_id}",
            intake_id=packet.intake_id,
            selected_vertical="block_insufficient_consent",
            route_reason="owner consent status is unknown; intake cannot proceed without manual consent clarification",
            blockers=["insufficient_consent"],
            can_generate_pilot_receipt=False,
        )
    if _has_forbidden_scope(packet):
        return PilotVerticalRoute(
            route_id=f"route-{packet.intake_id}",
            intake_id=packet.intake_id,
            selected_vertical="block_forbidden_artifact",
            route_reason="requested scope includes forbidden external action or live execution",
            blockers=["forbidden_external_action"],
            can_generate_pilot_receipt=False,
        )
    if packet.provided_artifact.raw_content_included and packet.provided_artifact.contains_private_data_declared is True:
        return PilotVerticalRoute(
            route_id=f"route-{packet.intake_id}",
            intake_id=packet.intake_id,
            selected_vertical="hold_manual_triage",
            route_reason="raw private data was declared; redacted local intake is required before routing",
            route_confidence="low",
            required_next_artifacts=["redacted manifest or redacted summary"],
            blockers=["raw_private_data_declared"],
            can_generate_pilot_receipt=False,
        )

    requested = packet.requested_vertical
    if artifact_type in AGENTSEC_ARTIFACTS:
        selected: SelectedVertical = "agentsec"
        reason = "MCP/tool manifest artifacts route to AgentSec Gate"
    elif artifact_type in QIRA_ARTIFACTS:
        selected = "qira"
        reason = "patch, diff, and CI summary artifacts route to QIRA-Code ReleaseGate"
    elif artifact_type in DATACAPSULE_ARTIFACTS:
        selected = "datacapsule"
        reason = "dataset, corpus, and dataset-card artifacts route to DataCapsule"
    elif artifact_type == "mixed":
        selected = "hold_manual_triage"
        reason = "mixed artifacts need manual triage before a single pilot vertical is selected"
        blockers.append("mixed_artifact")
    else:
        selected = "hold_manual_triage"
        reason = "unknown artifact type needs manual triage"
        blockers.append("unknown_artifact")

    if requested not in {"auto_route", "unknown"} and selected in {"agentsec", "qira", "datacapsule"} and requested != selected:
        selected = "hold_manual_triage"
        reason = "requested vertical conflicts with artifact-derived route"
        blockers.append("vertical_artifact_mismatch")

    return PilotVerticalRoute(
        route_id=f"route-{packet.intake_id}",
        intake_id=packet.intake_id,
        selected_vertical=selected,
        route_reason=reason,
        route_confidence="high" if selected in {"agentsec", "qira", "datacapsule"} else "medium",
        required_next_artifacts=[] if selected in {"agentsec", "qira", "datacapsule"} else ["clarified owner consent and redacted artifact summary"],
        blockers=blockers,
        can_generate_pilot_receipt=selected in {"agentsec", "qira", "datacapsule"} and not blockers,
    )


def route_to_jsonable(route: PilotVerticalRoute) -> dict[str, Any]:
    return route.model_dump(mode="json", by_alias=True)
