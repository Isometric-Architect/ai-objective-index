from pathlib import Path

from ai_objective_index.agent_adoption import repo_root
from ai_objective_index.agent_adoption.cdp_audit import run_cdp_audit


EXPECTED_ASSETS = [
    "agent_discovery/CAPABILITY_DECISION_PACKET_SPEC.md",
    "agent_discovery/ROUTE_SEMANTICS_SPEC.md",
    "agent_discovery/ROUTE_REASON_CODES.md",
    "agent_discovery/HOLD_TO_REPLAN_LOOP_SPEC.md",
    "agent_discovery/FRESHNESS_RUGPULL_NEGATIVE_CACHE_SPEC.md",
    "agent_discovery/FINAL_ARGUMENT_PREFLIGHT_SPEC.md",
    "agent_discovery/AGENT_MIDDLEWARE_CONTRACT.md",
    "agent_discovery/CAPABILITY_DECISION_PACKET_EXAMPLES.json",
    "agent_discovery/ROUTE_TRANSITION_EXAMPLES.json",
    "public_launch/aoi_agent_discovery_5/AOI_D5_AUDIT_RESULT.json",
    "docs/aoi_route_reason_codes.md",
    "docs/aoi_final_argument_preflight.md",
    "docs/aoi_agent_middleware_contract.md",
    "docs/aoi_d5_test_residual_repair.md",
]


def test_aoi_d5_assets_exist_after_audit_generation():
    run_cdp_audit(write_result=True)

    missing = [path for path in EXPECTED_ASSETS if not (repo_root() / Path(path)).exists()]
    assert not missing
