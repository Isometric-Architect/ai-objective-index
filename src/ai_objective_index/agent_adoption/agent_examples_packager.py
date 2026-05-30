from __future__ import annotations

from pathlib import Path
from typing import Any

from . import write_json, write_text
from .agent_staleness_policy import build_staleness_policy


def markdown_artifacts() -> dict[Path, str]:
    return {
        Path("agent_discovery") / "WHEN_TO_USE_AOI.md": """# When To Use AOI

Use AOI when an AI agent needs to discover source-traced MCP/tool/API candidates for an objective, compare useful options with missing fields visible, or run a pre-use trust route before recommending or using a candidate.

AOI is especially useful when ordinary agents might over-recommend, skip HOLD, confuse metadata with proof, or treat tool availability as tool authorization.
""",
        Path("agent_discovery") / "WHEN_NOT_TO_USE_AOI.md": """# When Not To Use AOI

Do not use AOI as a security certification system, provider verification service, legal/privacy/license/compliance clearance, purchase recommendation, live execution layer, or external action authorization system.

AOI does not buy, book, log in, send email, submit forms, mutate repositories, deploy, publish, upload data, train models, or use credentials.
""",
        Path("agent_discovery") / "AGENT_DISCOVER_MODE.md": """# AOI Agent Discover Mode

Discover mode helps ordinary AI agents find useful source-traced capability candidates quickly. It returns top candidates even when every candidate is HOLD, because HOLD should mean "useful but needs next action," not a dead end.

Each candidate includes source trace references, missing fields, a preliminary route decision, must-not-claim terms, freshness notes, and a ResidualOps escalation path.
""",
        Path("agent_discovery") / "AGENT_PREFLIGHT_MODE.md": """# AOI Agent Preflight Mode

Preflight mode runs before an agent recommends or uses a candidate. It separates `tool_available` from `tool_authorized`, and blocks or holds unsafe action claims.

It should be used before live tool execution, external mutation, publication, deployment, upload, training, or strong claims. Missing permission, privacy, policy, pricing, data-retention, or freshness fields become HOLD with next actions.
""",
        Path("agent_discovery") / "MCP_AGENT_PROMPTS.md": """# MCP Agent Prompts

Prompt:

```text
Use AOI to find the best source-traced MCP/tool/API candidates for this objective. Return top candidates first, then source traces, missing fields, route decisions, must-not-claim boundaries, freshness, and ResidualOps escalation. Do not execute tools based only on AOI output.
```

Preflight prompt:

```text
Use AOI preflight before recommending or using this candidate. Treat tool availability as separate from tool authorization. Return ALLOW/HOLD/BLOCK, missing fields, allowed next steps, forbidden next steps, and must-not-claim boundaries.
```
""",
        Path("agent_discovery") / "OPENAPI_AGENT_EXAMPLES.md": """# OpenAPI Agent Examples

This package provides request and response examples under `api/vnext/examples/agent/`.

AOI-AGENT-ADOPTION-2 wires the read-only local REST shapes for capability-card, discover, preflight, and adoption status. These endpoints reuse deterministic local helpers and do not add live network calls, external action execution, PyPI upload, MCP Registry publish, certification claims, product-readiness claims, or action authorization.
""",
        Path("agent_discovery") / "AGENT_CLAIM_BOUNDARY.md": """# AOI Agent Claim Boundary

- `candidate != verified`
- `metadata != proof`
- `tool_available != tool_authorized`
- `source_trace != security_certification`
- `route_decision != action_authorization`

AOI does not certify security, prove code correctness, clear legal/privacy/license/compliance status, guarantee quality, prove product readiness, or authorize external action.
""",
        Path("agent_discovery") / "FRESHNESS_AND_STALENESS_POLICY.md": """# Freshness And Staleness Policy

Agent outputs should include `last_checked_at`, `source_trace_age`, `registry_payload_version`, `stale_warning`, `needs_refresh`, and `refresh_next_action`.

Do not claim live freshness unless a live check was actually performed. Static sample records can support discovery, but preflight should HOLD stale or unclear metadata before external-facing recommendation.
""",
        Path("agent_discovery") / "ORDINARY_AGENT_FAILURE_MODES.md": """# Ordinary Agent Failure Modes

Ordinary agents may hallucinate candidates, over-recommend, skip HOLD, confuse tool availability with tool authorization, treat metadata as proof, treat README claims as verification, treat a registry listing as approval, or execute before policy checks.

AOI counters this by making discovery useful first, then requiring preflight before use. Discover mode keeps HOLD candidates visible with next actions. Preflight mode blocks external actions and overclaims. ResidualOps routes enterprise review to AgentSec, QIRA, DataCapsule, or the dashboard/share-pack layer.
""",
        Path("agent_discovery") / "PRIVATE_KERNEL_NONDISCLOSURE.md": """# Private Kernel Nondisclosure

AOI public artifacts may show schemas, source-trace fields, missing fields, ALLOW/HOLD/BLOCK labels, examples, and high-level ResidualOps routes.

Ranking weights remain private. Thresholds remain private. Provider priors remain private. Anti-gaming rules remain private. Private negative controls remain private. Private probe seeds remain private. Commercial routing policy remains private. Real feedback memory and customer-specific data remain private.
""",
        Path("examples") / "agent_prompts" / "discover_mcp_candidates.md": """# Discover MCP Candidates

Use AOI discover mode to find source-traced MCP/tool/API candidates for my objective. Return top candidates even if they are HOLD, with source trace references, missing fields, preliminary route decisions, next actions, must-not-claim boundaries, freshness, and ResidualOps escalation. Do not execute tools based only on discovery output.
""",
        Path("examples") / "agent_prompts" / "preflight_mcp_candidate.md": """# Preflight MCP Candidate

Use AOI preflight mode for this candidate before recommending or using it. Distinguish tool availability from tool authorization. Return ALLOW/HOLD/BLOCK, reason, missing fields, allowed next steps, forbidden next steps, must-not-claim boundaries, freshness, and ResidualOps escalation.
""",
        Path("examples") / "agent_prompts" / "residualops_escalation.md": """# ResidualOps Escalation

If the candidate risk is tool/manifest/permission-related, route to AgentSec. If it is code, CI, patch, or release-related, route to QIRA. If it is data, corpus, rights, privacy, license, or eval-leakage-related, route to DataCapsule. For portfolio receipt tracking, route to the ResidualOps dashboard.
""",
        Path("examples") / "agent_prompts" / "ordinary_agent_tool_selection_policy.md": """# Ordinary Agent Tool Selection Policy

Discover first. Preflight second. Claim boundary always.

Never treat candidate metadata as proof. Never treat a listed tool as authorized. Never execute, deploy, publish, upload, train, post, create issues, or call external APIs from AOI output alone.
""",
        Path("docs") / "aoi_agent_native_discovery.md": """# AOI Agent-Native Discovery

AOI is optimized for ordinary AI agents that need a source-traced way to find useful capability candidates. Discover mode returns candidates, source traces, missing fields, preliminary route decisions, freshness notes, and next actions without hiding HOLD.

This is AI-native capability discovery plus pre-use trust routing, not generic search and not automatic execution.
""",
        Path("docs") / "aoi_agent_preflight.md": """# AOI Agent Preflight

Preflight runs before an agent recommends or uses a candidate. It separates tool availability from tool authorization and blocks external action requests, credential handling, certification claims, and product-readiness claims.

Missing permission, privacy, retention, policy, pricing, or freshness fields produce HOLD with next action.
""",
        Path("docs") / "aoi_capability_card.md": """# AOI Capability Card

The AOI capability card is a machine-readable summary for agent discovery. It tells agents when AOI is useful, when it is not, what inputs and outputs discover/preflight modes expect, and which ResidualOps escalation route applies.
""",
        Path("docs") / "aoi_ordinary_agent_failure_modes.md": """# AOI Ordinary Agent Failure Modes

Ordinary agents may hallucinate candidates, over-recommend, skip HOLD, confuse availability with authorization, treat metadata as proof, or execute before policy checks. AOI addresses this by requiring source traces, missing fields, route decisions, next actions, and must-not-claim boundaries.
""",
        Path("docs") / "aoi_residualops_extension_map.md": """# AOI ResidualOps Extension Map

AOI is the public agent/developer discovery and pre-use router. ResidualOps is the enterprise/operator governance layer.

AgentSec covers tool and manifest risk. QIRA covers code and release risk. DataCapsule covers data and use-boundary risk. The ResidualOps dashboard covers portfolio receipt tracking and reviewer artifacts.
""",
        Path("docs") / "aoi_agent_claim_boundaries.md": """# AOI Agent Claim Boundaries

AOI output is not provider verification, security certification, code correctness proof, legal/privacy/license/compliance clearance, quality guarantee, product-readiness proof, or external action authorization.

Agents should carry `candidate != verified`, `metadata != proof`, `tool_available != tool_authorized`, and `route_decision != action_authorization` into every user-facing summary.
""",
        Path("docs") / "aoi_private_kernel_non_disclosure.md": """# AOI Private Kernel Non-Disclosure

Public AOI artifacts expose schemas, examples, source-trace concepts, missing-field language, and high-level ResidualOps routes.

Ranking weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, commercial routing policy, real feedback memory, and customer-specific data remain private and are not included.
""",
    }


def json_artifacts() -> dict[Path, dict[str, Any]]:
    return {
        Path("agent_discovery") / "FRESHNESS_AND_STALENESS_POLICY.json": build_staleness_policy(),
    }


def write_example_artifacts() -> dict[str, Any]:
    for path, text in markdown_artifacts().items():
        write_text(path, text)
    for path, payload in json_artifacts().items():
        write_json(path, payload)
    return {"markdown_count": len(markdown_artifacts()), "json_count": len(json_artifacts())}
