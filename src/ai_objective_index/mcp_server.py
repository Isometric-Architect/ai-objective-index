from __future__ import annotations

from typing import Any

from . import mcp_tools
from .mcp_manifest import get_mcp_tool_manifest


try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover - exercised by runtime smoke command.
    FastMCP = None  # type: ignore[assignment]


def _build_fastmcp_server() -> Any:
    if FastMCP is None:
        return None

    server = FastMCP("ai-objective-index")

    @server.tool()
    def search_objectives(
        query: str,
        domain: str | None = None,
        objective: str | None = None,
        constraints: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search local AOI sample objects and return read-only scored candidates."""
        return mcp_tools.search_objectives(
            query=query,
            domain=domain,
            objective=objective,
            constraints=constraints,
            limit=limit,
        )

    @server.tool()
    def rank_options(
        options: list[dict[str, Any]],
        objective: str,
        constraints: dict[str, Any] | None = None,
        scoring_profile: str = "default",
    ) -> dict[str, Any]:
        """Rank provided options without crawling URLs or calling networks."""
        return mcp_tools.rank_options(
            options=options,
            objective=objective,
            constraints=constraints,
            scoring_profile=scoring_profile,
        )

    @server.tool()
    def compare_tools(
        tool_ids: list[str],
        compare_fields: list[str] | None = None,
        query: str | None = None,
        objective: str | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compare local AOI tools side by side."""
        return mcp_tools.compare_tools(
            tool_ids=tool_ids,
            compare_fields=compare_fields,
            query=query,
            objective=objective,
            constraints=constraints,
        )

    @server.tool()
    def explain_score(object_id: str) -> dict[str, Any]:
        """Explain one local object's objective-fit score."""
        return mcp_tools.explain_score(object_id=object_id)

    @server.tool()
    def get_source_trace(object_id: str, field: str | None = None) -> dict[str, Any]:
        """Return local source traces for an object and optional field."""
        return mcp_tools.get_source_trace(object_id=object_id, field=field)

    @server.tool()
    def list_missing_fields(object_id: str) -> dict[str, Any]:
        """Return missing-field guidance for one local AOI object."""
        return mcp_tools.list_missing_fields(object_id=object_id)

    @server.tool()
    def generate_decision_receipt(
        query: str,
        selected_object_id: str,
        alternatives: list[str] | None = None,
        objective: str | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a read-only decision receipt without external actions."""
        return mcp_tools.generate_decision_receipt(
            query=query,
            selected_object_id=selected_object_id,
            alternatives=alternatives,
            objective=objective,
            constraints=constraints,
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

    return server


def main() -> None:
    server = _build_fastmcp_server()
    if server is None:
        print("MCP SDK not installed. Tool functions and manifest are available.")
        manifest = get_mcp_tool_manifest()
        print(f"server_name: {manifest['server_name']}")
        print("tools: " + ", ".join(tool["name"] for tool in manifest["tools"]))
        return

    server.run()


if __name__ == "__main__":
    main()
