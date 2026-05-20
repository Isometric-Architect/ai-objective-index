from pydantic import ValidationError
import pytest

from ai_objective_index.vnext import ResidualCredit


def test_vnext_residual_credit_scores_are_bounded():
    credit = ResidualCredit(
        capability_id="cap-pytest",
        objective_scope="test_generation",
        raw_success_score=0.8,
        eco_success_score=0.7,
        negative_control_score=0.9,
        security_risk=0.2,
        context_burden=0.3,
        integration_reliability=0.8,
        known_failure_similarity=0.1,
        freshness=0.9,
    )

    assert credit.model_dump(by_alias=True)["schema"] == "aoi.vnext.residual_credit.v0_3"

    with pytest.raises(ValidationError):
        ResidualCredit(
            capability_id="cap-bad",
            objective_scope="x",
            raw_success_score=1.2,
            eco_success_score=0.7,
            negative_control_score=0.9,
            security_risk=0.2,
            context_burden=0.3,
            integration_reliability=0.8,
            known_failure_similarity=0.1,
            freshness=0.9,
        )
