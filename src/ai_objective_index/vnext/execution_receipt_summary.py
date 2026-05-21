from __future__ import annotations

from collections import Counter

from .execution_receipt_loop import (
    CapabilityReceiptMemory,
    ObjectiveReceiptSummary,
    StoredExecutionReceipt,
)


FAILURE_OUTCOMES = {"fail", "blocked"}


def build_capability_receipt_memory(
    capability_id: str,
    records: list[StoredExecutionReceipt],
) -> CapabilityReceiptMemory:
    relevant = [record for record in records if record.receipt.capability_id == capability_id]
    if not relevant:
        return CapabilityReceiptMemory(
            capability_id=capability_id,
            memory_status="NO_RECEIPTS",
            can_influence_route=False,
        )
    outcomes = Counter(record.receipt.outcome for record in relevant)
    errors = Counter(record.receipt.error_type for record in relevant if record.receipt.error_type)
    failures = [
        record.receipt.outcome_summary
        for record in relevant
        if record.receipt.outcome in FAILURE_OUTCOMES and record.receipt.outcome_summary
    ][:10]
    residuals = [
        note
        for record in relevant
        for note in record.receipt.residual_notes
        if note
    ][:10]
    origins = sorted({record.receipt.receipt_origin for record in relevant})
    if any(outcome in outcomes for outcome in FAILURE_OUTCOMES) and any(outcome in outcomes for outcome in {"success", "partial"}):
        status = "MIXED_SIGNALS"
    elif any(outcome in outcomes for outcome in FAILURE_OUTCOMES):
        status = "FAILURE_SIGNALS"
    elif len(relevant) < 2:
        status = "HOLD_INSUFFICIENT_RECEIPTS"
    else:
        status = "RECEIPTS_AVAILABLE"
    return CapabilityReceiptMemory(
        capability_id=capability_id,
        receipt_count=len(relevant),
        outcome_counts=dict(outcomes),
        last_outcome=relevant[-1].receipt.outcome,
        known_failures=failures,
        recurring_error_types=[name for name, count in errors.most_common() if count >= 1 and name],
        residual_notes=residuals,
        evidence_origins=origins,
        can_influence_route=any(record.validation.can_influence_route for record in relevant),
        memory_status=status,
    )


def build_objective_receipt_summary(
    objective_id: str,
    records: list[StoredExecutionReceipt],
) -> ObjectiveReceiptSummary:
    relevant = [record for record in records if record.receipt.objective_id == objective_id]
    outcomes = Counter(record.receipt.outcome for record in relevant)
    errors = Counter(record.receipt.error_type for record in relevant if record.receipt.error_type)
    notes = []
    if not relevant:
        notes.append("No local receipt memory is available for this objective.")
    elif any(outcome in outcomes for outcome in FAILURE_OUTCOMES):
        notes.append("Failure receipts should add warning or downgrade signals; they do not certify alternatives.")
    else:
        notes.append("Receipt memory can add context but cannot upgrade a route into verification or certification.")
    return ObjectiveReceiptSummary(
        objective_id=objective_id,
        receipt_count=len(relevant),
        capabilities_seen=sorted({record.receipt.capability_id for record in relevant}),
        outcome_counts=dict(outcomes),
        top_failure_modes=[name for name, _ in errors.most_common(5) if name],
        route_adjustment_notes=notes,
    )
