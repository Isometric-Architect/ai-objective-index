from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack
from ai_objective_index.portfolio.external_share_pack_distribution_gate import run_distribution_gate


def test_distribution_gate_allows_static_modes():
    generate_external_share_pack(write_result=True)
    assert run_distribution_gate("local_static_demo_zip", write_result=True)["decision"] == "PASS_ALLOWED_STATIC_SHARE"
    assert run_distribution_gate("internal_review", write_result=False)["decision"] == "PASS_ALLOWED_STATIC_SHARE"


def test_distribution_gate_blocks_live_or_production_modes():
    generate_external_share_pack(write_result=True)
    assert run_distribution_gate("live_connector_demo", write_result=False)["decision"] == "BLOCK_DISTRIBUTION_MODE"
    assert run_distribution_gate("production_deployment", write_result=False)["decision"] == "BLOCK_DISTRIBUTION_MODE"
    assert run_distribution_gate("security_certification_claim", write_result=False)["decision"] == "BLOCK_DISTRIBUTION_MODE"
