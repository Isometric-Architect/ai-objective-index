from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _write_json

from .mcp_manifest_hardening import write_mcp_manifest_hardening_result
from .profile_pack import OUTPUT_DIR, write_profile_pack


PACKAGE_RESULT_PATH = OUTPUT_DIR / "AGENTSEC4_PACKAGE_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "AGENTSEC4_NEXT_STEPS.md"


def _write_text(path: Path, text: str) -> Path:
    from ai_objective_index.real_pypi_upload_gate import _repo_root

    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def build_agentsec4_package_result(profile_pack: dict[str, Any], hardening: dict[str, Any]) -> dict[str, Any]:
    if hardening["decision"].startswith("BLOCK"):
        decision = "BLOCK_AGENTSEC4_MCP_MANIFEST_RISK"
    elif hardening["decision"].startswith("HOLD"):
        decision = "HOLD_AGENTSEC4_REVIEW_REQUIRED"
    else:
        decision = "PASS_AGENTSEC4_POLICY_PACK_AND_MCP_HARDENING"
    return {
        "schema": "AgentSec4_PackageResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "profile_pack_decision": profile_pack["decision"],
        "mcp_manifest_hardening_decision": hardening["decision"],
        "profile_count": profile_pack["profile_count"],
        "tool_count": hardening["tool_count"],
        "known_limits": [
            "local policy profile and static MCP manifest hardening only",
            "no live MCP call",
            "no external tool execution",
            "no URL fetch",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not action authorization",
        ],
        "must_not_claim": [
            "do not claim verified tool status",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim live gateway protection",
            "do not claim external action authorization",
            "do not claim legal compliance",
        ],
        "external_actions_performed": False,
        "network_used": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "token_printed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
    }


def write_next_steps(result: dict[str, Any]) -> Path:
    return _write_text(
        NEXT_STEPS_PATH,
        f"""# AgentSec-4 Next Steps

Decision: `{result['decision']}`

1. Use the profile pack as public-safe policy presets for local MCP/tool metadata review.
2. Keep exact private thresholds, provider priors, anti-gaming rules, and private negative controls outside the public repository.
3. Feed AgentSec-4 status into the ResidualOps dashboard before enabling any external discovery surface.
4. Treat static manifest PASS as a local hardening signal only, not security certification or action authorization.
""",
    )


def run_agentsec4_package() -> dict[str, Any]:
    profile_pack = write_profile_pack()
    hardening = write_mcp_manifest_hardening_result()
    result = build_agentsec4_package_result(profile_pack, hardening)
    _write_json(PACKAGE_RESULT_PATH, result)
    write_next_steps(result)
    return result


def main() -> None:
    result = run_agentsec4_package()
    print(f"agentsec4_package: {result['decision']} profiles={result['profile_count']} tools={result['tool_count']}")


if __name__ == "__main__":
    main()
