from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .models import AgentSecPolicyProfile
from .policy_gate import developer_default_profile, strict_enterprise_profile


OUTPUT_DIR = Path("public_launch") / "agentsec4"
PROFILE_PACK_PATH = OUTPUT_DIR / "AGENTSEC4_PROFILE_PACK.json"
PROFILE_PACK_REPORT_PATH = OUTPUT_DIR / "AGENTSEC4_PROFILE_PACK.md"


def local_metadata_only_profile() -> AgentSecPolicyProfile:
    return AgentSecPolicyProfile(
        profile_id="agentsec-local-metadata-only",
        name="AgentSec local metadata only policy",
        mode="local_metadata_only",
        require_namespace=False,
        hold_on_network_access=False,
        hold_on_file_access=False,
        hold_on_write_access=True,
        hold_on_secret_access=True,
        hold_on_browser_access=False,
        hold_on_code_execution=True,
        hold_on_hidden_instruction=True,
        block_on_forbidden_action=True,
        block_on_unsupported_claim=True,
    )


def ci_artifact_review_profile() -> AgentSecPolicyProfile:
    return AgentSecPolicyProfile(
        profile_id="agentsec-ci-artifact-review",
        name="AgentSec CI artifact review policy",
        mode="developer_default",
        require_namespace=True,
        hold_on_network_access=True,
        hold_on_file_access=True,
        hold_on_write_access=True,
        hold_on_secret_access=True,
        hold_on_browser_access=True,
        hold_on_code_execution=True,
        hold_on_hidden_instruction=True,
        block_on_forbidden_action=True,
        block_on_unsupported_claim=True,
    )


def mcp_registry_metadata_profile() -> AgentSecPolicyProfile:
    return AgentSecPolicyProfile(
        profile_id="agentsec-mcp-registry-metadata",
        name="AgentSec MCP Registry metadata policy",
        mode="developer_default",
        require_namespace=True,
        hold_on_network_access=True,
        hold_on_file_access=True,
        hold_on_write_access=True,
        hold_on_secret_access=True,
        hold_on_browser_access=True,
        hold_on_code_execution=True,
        hold_on_hidden_instruction=True,
        block_on_forbidden_action=True,
        block_on_unsupported_claim=True,
    )


def build_profile_pack() -> dict[str, Any]:
    profiles = [
        local_metadata_only_profile(),
        developer_default_profile(),
        ci_artifact_review_profile(),
        mcp_registry_metadata_profile(),
        strict_enterprise_profile(),
    ]
    payloads = [profile.model_dump(mode="json", by_alias=True) for profile in profiles]
    return {
        "schema": "AgentSec_ProfilePack/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": "PASS_AGENTSEC4_PROFILE_PACK_READY",
        "profile_count": len(payloads),
        "profiles": payloads,
        "public_policy_shape": [
            "profile identity",
            "permission hold flags",
            "forbidden action block flags",
            "unsupported claim block flags",
            "local-only/no-network/no-live-MCP/no-action-authorization flags",
        ],
        "private_kernel_reserved": [
            "exact risk weights",
            "exact thresholds",
            "provider trust priors",
            "anti-gaming rules",
            "private negative-control seeds",
            "commercial routing policy",
        ],
        "external_actions_performed": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "network_used": False,
        "token_printed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
    }


def build_profile_pack_markdown(pack: dict[str, Any]) -> str:
    rows = "\n".join(
        "| `{profile_id}` | `{mode}` | `{namespace}` | `{write}` | `{secret}` | `{code}` |".format(
            profile_id=profile["profile_id"],
            mode=profile["mode"],
            namespace=profile["require_namespace"],
            write=profile["hold_on_write_access"],
            secret=profile["hold_on_secret_access"],
            code=profile["hold_on_code_execution"],
        )
        for profile in pack["profiles"]
    )
    return f"""# AgentSec-4 Profile Pack

Decision: `{pack['decision']}`

AgentSec-4 exposes public-safe policy profile shapes for local MCP/tool metadata review.

| Profile | Mode | Namespace Review | Hold Write | Hold Secret | Hold Code Execution |
| --- | --- | --- | --- | --- | --- |
{rows}

## Boundary

The profile pack is not a security certification, quality guarantee, product-readiness claim, or action authorization system. It does not call live MCP servers, execute tools, fetch URLs, request tokens, or expose exact private weights, thresholds, provider priors, anti-gaming rules, private negative-control seeds, or commercial routing policy.
"""


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def write_profile_pack() -> dict[str, Any]:
    pack = build_profile_pack()
    _write_json(PROFILE_PACK_PATH, pack)
    _write_text(PROFILE_PACK_REPORT_PATH, build_profile_pack_markdown(pack))
    return pack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write AgentSec-4 public-safe policy profile pack.")
    parser.add_argument("--write-sample", action="store_true", help="Write AgentSec-4 profile pack outputs.")
    return parser


def main() -> None:
    build_parser().parse_args()
    result = write_profile_pack()
    print(f"agentsec4_profile_pack: {result['decision']} profiles={result['profile_count']}")


if __name__ == "__main__":
    main()
