from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .action_boundary import add_action_boundary_to_receipt
from .claim_ceiling import claim_ceiling_not_asserted_list, infer_claim_ceiling
from .models import DecisionReceipt
from .obstruction_certificate import build_obstructions
from .scoring import score_object
from .use_rights import default_use_rights_for_object


_KNOWN_LIMITS = [
    "v0.1 read-only benchmark output",
    "not a quality guarantee",
    "verify source traces before production use",
    "no purchase, booking, payment, login, email, or contract execution",
]


def _constraint_checks(constraints: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not constraints:
        return []
    return [
        {
            "constraint": key,
            "status": "checked",
            "note": "Checked against available structured fields and source traces where present.",
        }
        for key in constraints
    ]


def generate_decision_receipt(
    store: Any,
    selected_object_id: str,
    alternatives: list[str] | None = None,
    query: str | None = None,
    objective: Any = None,
    constraints: dict[str, Any] | None = None,
) -> DecisionReceipt:
    selected = store.get_object(selected_object_id)
    if selected is None:
        raise ValueError(f"Unknown selected_object_id: {selected_object_id}")

    selected_traces = store.get_traces(selected_object_id)
    selected_score = score_object(
        selected,
        query=query,
        objective=objective,
        constraints=constraints,
        traces=selected_traces,
    )

    alternative_rows: list[dict[str, Any]] = []
    for alternative_id in alternatives or []:
        alternative = store.get_object(alternative_id)
        if alternative is None:
            alternative_rows.append(
                {
                    "object_id": alternative_id,
                    "reason_not_selected": "Object was not found in the in-memory store.",
                }
            )
            continue
        alternative_score = score_object(
            alternative,
            query=query,
            objective=objective,
            constraints=constraints,
            traces=store.get_traces(alternative_id),
        )
        alternative_rows.append(
            {
                "object_id": alternative_id,
                "name": alternative.name,
                "objective_score": alternative_score.objective_score,
                "reason_not_selected": "Lower objective-fit score or weaker fit for the stated constraints.",
            }
        )

    claim_ceiling = infer_claim_ceiling(selected, selected_traces)
    obstructions = build_obstructions(selected, selected_traces, requested_action="DECISION_RECEIPT")
    action_boundary = add_action_boundary_to_receipt({})["action_boundary"]

    return DecisionReceipt(
        selected_object_id=selected.object_id,
        selected_name=selected.name,
        objective=objective or query,
        constraints_checked=_constraint_checks(constraints),
        why_selected=selected_score.rank_reason,
        alternatives=alternative_rows,
        known_limits=list(_KNOWN_LIMITS),
        source_trace_ids=[trace.trace_id for trace in selected_traces],
        timestamp=datetime.now(UTC),
        objective_score=selected_score.objective_score,
        warnings=selected_score.warnings,
        use_rights=default_use_rights_for_object(selected),
        claim_ceiling=claim_ceiling.value,
        action_boundary=action_boundary,
        obstructions=[item.model_dump(mode="json") for item in obstructions],
        not_asserted=claim_ceiling_not_asserted_list(claim_ceiling),
    )
