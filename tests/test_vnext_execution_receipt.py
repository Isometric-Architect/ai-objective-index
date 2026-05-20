from datetime import UTC, datetime

from pydantic import ValidationError
import pytest

from ai_objective_index.vnext import ExecutionReceipt


def test_vnext_execution_receipt_validates_outcome():
    receipt = ExecutionReceipt(
        receipt_id="rec-1",
        objective_id="obj-1",
        capability_id="cap-1",
        agent_id_hash="agent-hash",
        environment_class="local",
        outcome="hold",
        timestamp=datetime.now(UTC),
    )

    assert receipt.model_dump(by_alias=True)["outcome"] == "hold"

    with pytest.raises(ValidationError):
        ExecutionReceipt(
            receipt_id="rec-2",
            objective_id="obj-1",
            capability_id="cap-1",
            agent_id_hash="agent-hash",
            environment_class="local",
            outcome="maybe",
            timestamp=datetime.now(UTC),
        )
