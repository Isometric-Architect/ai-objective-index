from __future__ import annotations

from typing import Any

from . import mcp_tools
from .mcp_compat import fetch as compat_fetch
from .mcp_compat import search as compat_search
from .mcp_manifest import get_mcp_tool_manifest


FALLBACK_MESSAGE = "MCP SDK not installed. Use mcp_tools functions, manifest, or install optional dependency."

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - depends on optional local dependency.
    FastMCP = None  # type: ignore[assignment]


def mcp_sdk_available() -> bool:
    return FastMCP is not None


def runtime_status() -> dict[str, Any]:
    manifest = get_mcp_tool_manifest()
    return {
        "server_name": manifest["server_name"],
        "mcp_sdk_available": mcp_sdk_available(),
        "read_only": True,
        "fallback_message": None if mcp_sdk_available() else FALLBACK_MESSAGE,
        "tools": [tool["name"] for tool in manifest["tools"]],
        "forbidden_actions": manifest["forbidden_actions"],
    }


def build_server() -> Any:
    if FastMCP is None:
        return None

    server = FastMCP("ai-objective-index")

    @server.tool()
    def search(query: str, data_scope: str = "sample", limit: int = 10) -> dict[str, Any]:
        """Generic read-only AOI search wrapper."""
        return compat_search(query=query, data_scope=data_scope, limit=limit)

    @server.tool()
    def fetch(object_id: str, data_scope: str = "sample") -> dict[str, Any]:
        """Generic read-only AOI object fetch wrapper."""
        return compat_fetch(object_id=object_id, data_scope=data_scope)

    @server.tool()
    def search_objectives(
        query: str,
        domain: str | None = None,
        objective: str | None = None,
        constraints: dict[str, Any] | None = None,
        limit: int = 10,
        data_scope: str = "sample",
    ) -> dict[str, Any]:
        """Search local AOI objects and return scored candidates."""
        return mcp_tools.search_objectives(
            query=query,
            domain=domain,
            objective=objective,
            constraints=constraints,
            limit=limit,
            data_scope=data_scope,
        )

    @server.tool()
    def rank_options(
        options: list[dict[str, Any]],
        objective: str,
        constraints: dict[str, Any] | None = None,
        scoring_profile: str = "default",
        data_scope: str = "sample",
    ) -> dict[str, Any]:
        """Rank provided options without crawling URLs."""
        return mcp_tools.rank_options(
            options=options,
            objective=objective,
            constraints=constraints,
            scoring_profile=scoring_profile,
            data_scope=data_scope,
        )

    @server.tool()
    def compare_tools(
        tool_ids: list[str],
        compare_fields: list[str] | None = None,
        query: str | None = None,
        objective: str | None = None,
        constraints: dict[str, Any] | None = None,
        data_scope: str = "sample",
    ) -> dict[str, Any]:
        """Compare local AOI tools side by side."""
        return mcp_tools.compare_tools(
            tool_ids=tool_ids,
            compare_fields=compare_fields,
            query=query,
            objective=objective,
            constraints=constraints,
            data_scope=data_scope,
        )

    @server.tool()
    def explain_score(object_id: str, data_scope: str = "sample") -> dict[str, Any]:
        """Explain one local object's objective-fit score."""
        return mcp_tools.explain_score(object_id=object_id, data_scope=data_scope)

    @server.tool()
    def get_source_trace(
        object_id: str,
        field: str | None = None,
        data_scope: str = "sample",
    ) -> dict[str, Any]:
        """Return local source traces for an object and optional field."""
        return mcp_tools.get_source_trace(object_id=object_id, field=field, data_scope=data_scope)

    @server.tool()
    def list_missing_fields(object_id: str, data_scope: str = "sample") -> dict[str, Any]:
        """Return missing-field guidance for one local AOI object."""
        return mcp_tools.list_missing_fields(object_id=object_id, data_scope=data_scope)

    @server.tool()
    def generate_decision_receipt(
        query: str,
        selected_object_id: str,
        alternatives: list[str] | None = None,
        objective: str | None = None,
        constraints: dict[str, Any] | None = None,
        data_scope: str = "sample",
    ) -> dict[str, Any]:
        """Generate a read-only decision receipt without external actions."""
        return mcp_tools.generate_decision_receipt(
            query=query,
            selected_object_id=selected_object_id,
            alternatives=alternatives,
            objective=objective,
            constraints=constraints,
            data_scope=data_scope,
        )

    @server.tool()
    def route_objective(
        query: str,
        objective: str,
        domain: str = "mcp_servers",
        data_scope: str = "sample",
        limit: int = 10,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Route an objective to local capability candidates without probes or network fetch."""
        return mcp_tools.route_objective(
            query=query,
            objective=objective,
            domain=domain,
            data_scope=data_scope,
            limit=limit,
            constraints=constraints,
        )

    @server.tool()
    def get_capability_trust(capability_id: str, data_scope: str = "sample") -> dict[str, Any]:
        """Return one vNext CapabilityTrustCard."""
        return mcp_tools.get_capability_trust(capability_id=capability_id, data_scope=data_scope)

    @server.tool()
    def explain_route_decision(
        capability_id: str,
        objective: str | None = None,
        data_scope: str = "sample",
    ) -> dict[str, Any]:
        """Explain one vNext route decision."""
        return mcp_tools.explain_route_decision(
            capability_id=capability_id,
            objective=objective,
            data_scope=data_scope,
        )

    @server.tool()
    def submit_execution_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
        """Store a local execution receipt; no external action is performed."""
        return mcp_tools.submit_execution_receipt(receipt=receipt)

    @server.tool()
    def get_execution_receipt(receipt_id: str) -> dict[str, Any]:
        """Read one local execution receipt by id."""
        return mcp_tools.get_execution_receipt(receipt_id=receipt_id)

    @server.tool()
    def list_capability_receipts(capability_id: str, limit: int = 20) -> dict[str, Any]:
        """List local receipt memory for one capability."""
        return mcp_tools.list_capability_receipts(capability_id=capability_id, limit=limit)

    @server.tool()
    def get_capability_receipt_memory(capability_id: str) -> dict[str, Any]:
        """Summarize local receipt memory for one capability."""
        return mcp_tools.get_capability_receipt_memory(capability_id=capability_id)

    @server.tool()
    def route_objective_with_receipts(
        query: str,
        objective: str,
        domain: str = "mcp_servers",
        data_scope: str = "sample",
        limit: int = 10,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Route an objective with local receipt-memory overlay; no probes or external execution."""
        return mcp_tools.route_objective_with_receipts(
            query=query,
            objective=objective,
            domain=domain,
            data_scope=data_scope,
            limit=limit,
            constraints=constraints,
        )

    @server.tool()
    def plan_probe_before_use(
        query: str,
        objective: str,
        data_scope: str = "sample",
        limit: int = 5,
        domain: str = "mcp_servers",
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Plan local metadata probes before use; no live MCP call or external execution."""
        return mcp_tools.plan_probe_before_use(
            query=query,
            objective=objective,
            data_scope=data_scope,
            limit=limit,
            domain=domain,
            constraints=constraints,
        )

    @server.tool()
    def run_local_probe_plan(plan: dict[str, Any] | None = None, plan_id: str | None = None) -> dict[str, Any]:
        """Run deterministic local metadata probes only."""
        return mcp_tools.run_local_probe_plan(plan=plan, plan_id=plan_id)

    @server.tool()
    def get_probe_receipt(receipt_id: str) -> dict[str, Any]:
        """Read one local probe receipt by id."""
        return mcp_tools.get_probe_receipt(receipt_id=receipt_id)

    @server.tool()
    def get_capability_probe_memory(capability_id: str) -> dict[str, Any]:
        """Summarize local probe memory for one capability."""
        return mcp_tools.get_capability_probe_memory(capability_id=capability_id)

    @server.tool()
    def route_objective_with_probes(
        query: str,
        objective: str,
        data_scope: str = "sample",
        limit: int = 5,
        domain: str = "mcp_servers",
        constraints: dict[str, Any] | None = None,
        run_local_probes: bool = False,
    ) -> dict[str, Any]:
        """Route an objective with local probe overlay; probe pass is not verification."""
        return mcp_tools.route_objective_with_probes(
            query=query,
            objective=objective,
            data_scope=data_scope,
            limit=limit,
            domain=domain,
            constraints=constraints,
            run_local_probes=run_local_probes,
        )

    @server.tool()
    def get_aoi_capability_card() -> dict[str, Any]:
        """Return the AOI agent capability card; read-only and local."""
        return mcp_tools.get_aoi_capability_card()

    @server.tool()
    def discover_capabilities_for_objective(
        objective: str,
        query: str,
        data_scope: str = "sample",
        desired_capability_type: str = "mcp_or_api",
        freshness_preference: str = "prefer_recent_source_traces_but_keep_hold_candidates_visible",
    ) -> dict[str, Any]:
        """Discover source-traced candidates with missing fields and next actions."""
        return mcp_tools.discover_capabilities_for_objective(
            objective=objective,
            query=query,
            data_scope=data_scope,
            desired_capability_type=desired_capability_type,
            freshness_preference=freshness_preference,
        )

    @server.tool()
    def preflight_capability_for_use(
        candidate_id: str,
        intended_use: str,
        available_metadata: dict[str, Any] | None = None,
        required_permissions: list[str] | None = None,
        organization_policy_optional: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Preflight one candidate before recommendation or use."""
        return mcp_tools.preflight_capability_for_use(
            candidate_id=candidate_id,
            intended_use=intended_use,
            available_metadata=available_metadata,
            required_permissions=required_permissions,
            organization_policy_optional=organization_policy_optional,
        )

    @server.tool()
    def explain_aoi_agent_use() -> dict[str, Any]:
        """Explain when ordinary agents should and should not use AOI."""
        return mcp_tools.explain_aoi_agent_use()

    @server.tool()
    def list_aoi_agent_examples() -> dict[str, Any]:
        """List local AOI agent examples and prompts."""
        return mcp_tools.list_aoi_agent_examples()

    return server


def print_fallback_summary() -> None:
    manifest = get_mcp_tool_manifest()
    print(FALLBACK_MESSAGE)
    print(f"server_name: {manifest['server_name']}")
    print(f"read_only: {manifest['read_only']}")
    print("tools: " + ", ".join(tool["name"] for tool in manifest["tools"]))


def run_stdio() -> bool:
    server = build_server()
    if server is None:
        print_fallback_summary()
        return False
    server.run()
    return True
