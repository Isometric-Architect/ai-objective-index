from ai_objective_index.portfolio.external_share_refresh_builder import generate_external_share_refresh
from ai_objective_index.portfolio.external_share_refresh_distribution_gate import run_refresh_distribution_gate


def test_external_share_refresh_distribution_gate_allows_static_modes():
    generate_external_share_refresh(write_result=True)
    assert run_refresh_distribution_gate("local_static_demo_zip", write_result=True)["decision"] == "PASS_ALLOWED_STATIC_SHARE"
    assert run_refresh_distribution_gate("internal_review", write_result=False)["decision"] == "PASS_ALLOWED_STATIC_SHARE"


def test_external_share_refresh_distribution_gate_blocks_unsafe_modes():
    generate_external_share_refresh(write_result=True)
    assert run_refresh_distribution_gate("live_connector_demo", write_result=False)["decision"] == "BLOCK_DISTRIBUTION_MODE"
    assert run_refresh_distribution_gate("production_deployment", write_result=False)["decision"] == "BLOCK_DISTRIBUTION_MODE"
    assert run_refresh_distribution_gate("public_certification_claim", write_result=False)["decision"] == "BLOCK_DISTRIBUTION_MODE"
