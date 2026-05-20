from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FORBIDDEN_ACTIONS = [
    "payment",
    "booking",
    "login",
    "email_sending",
    "form_submission",
    "purchase",
    "contract_signing",
    "account_connection",
]


def _schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": required or [],
        "properties": properties,
    }


def get_mcp_tool_manifest() -> dict[str, Any]:
    text = {"type": "string"}
    optional_text = {"type": ["string", "null"]}
    constraints = {"type": "object", "additionalProperties": True}
    data_scope = {
        "type": "string",
        "enum": [
            "sample",
            "generated",
            "integrated",
            "curated",
            "public_beta",
            "mcp_registry",
            "public_beta_mcp",
        ],
        "default": "sample",
        "description": "Local AOI data scope. Default remains sample.",
    }

    tools = [
        {
            "name": "search",
            "description": "Generic read-only MCP compatibility search wrapper over local AOI data scopes.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "query": text,
                    "data_scope": data_scope,
                    "limit": {"type": "integer", "default": 10, "minimum": 1},
                },
                ["query"],
            ),
            "output_schema": _schema(
                {
                    "results": {"type": "array"},
                    "read_only": {"const": True},
                    "data_scope": text,
                    "limitations": {"type": "array"},
                }
            ),
        },
        {
            "name": "fetch",
            "description": "Generic read-only MCP compatibility fetch wrapper returning one AOI object with score, traces, and missing fields.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "object_id": text,
                    "data_scope": data_scope,
                },
                ["object_id"],
            ),
            "output_schema": _schema(
                {
                    "object": {"type": "object"},
                    "score": {"type": "object"},
                    "source_traces": {"type": "array"},
                    "read_only": {"const": True},
                    "data_scope": text,
                }
            ),
        },
        {
            "name": "search_objectives",
            "description": "Search the local read-only AOI data scope and return scored objective-fit candidates.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "query": text,
                    "domain": optional_text,
                    "objective": optional_text,
                    "constraints": constraints,
                    "limit": {"type": "integer", "default": 10, "minimum": 1},
                    "data_scope": data_scope,
                },
                ["query"],
            ),
            "output_schema": _schema({"results": {"type": "array"}, "read_only": {"const": True}, "data_scope": text}),
        },
        {
            "name": "rank_options",
            "description": "Rank provided option names against an objective using local AOI data-scope matches or conservative placeholders.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "options": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": True,
                            "required": ["name"],
                            "properties": {
                                "name": text,
                                "url": optional_text,
                                "description": optional_text,
                            },
                        },
                    },
                    "objective": text,
                    "constraints": constraints,
                    "scoring_profile": {
                        "type": "string",
                        "enum": [
                            "default",
                            "cost_sensitive",
                            "privacy_sensitive",
                            "developer_friendly",
                            "commercial_use",
                        ],
                        "default": "default",
                    },
                    "data_scope": data_scope,
                },
                ["options", "objective"],
            ),
            "output_schema": _schema({"results": {"type": "array"}, "read_only": {"const": True}, "data_scope": text}),
        },
        {
            "name": "compare_tools",
            "description": "Compare local AOI objects side by side using Package 1 comparison and scoring.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "tool_ids": {"type": "array", "items": text},
                    "compare_fields": {"type": "array", "items": text},
                    "query": optional_text,
                    "objective": optional_text,
                    "constraints": constraints,
                    "data_scope": data_scope,
                },
                ["tool_ids"],
            ),
            "output_schema": _schema(
                {
                    "comparison_table": {"type": "array"},
                    "score_summary": {"type": "array"},
                    "read_only": {"const": True},
                    "data_scope": text,
                }
            ),
        },
        {
            "name": "explain_score",
            "description": "Explain one local object's objective-fit score, components, penalties, warnings, and trace ids.",
            "read_only": True,
            "input_schema": _schema({"object_id": text, "data_scope": data_scope}, ["object_id"]),
            "output_schema": _schema(
                {
                    "object_id": text,
                    "objective_score": {"type": "number"},
                    "rank_reason": {"type": "array"},
                    "read_only": {"const": True},
                    "data_scope": text,
                }
            ),
        },
        {
            "name": "get_source_trace",
            "description": "Return source traces for an object id and optional field filter.",
            "read_only": True,
            "input_schema": _schema({"object_id": text, "field": optional_text, "data_scope": data_scope}, ["object_id"]),
            "output_schema": _schema({"traces": {"type": "array"}, "read_only": {"const": True}, "data_scope": text}),
        },
        {
            "name": "list_missing_fields",
            "description": "Return missing or weak fields with why-it-matters guidance.",
            "read_only": True,
            "input_schema": _schema({"object_id": text, "data_scope": data_scope}, ["object_id"]),
            "output_schema": _schema(
                {"missing_fields": {"type": "array"}, "read_only": {"const": True}, "data_scope": text}
            ),
        },
        {
            "name": "generate_decision_receipt",
            "description": "Generate a read-only decision receipt without external action execution.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "query": text,
                    "selected_object_id": text,
                    "alternatives": {"type": "array", "items": text},
                    "objective": optional_text,
                    "constraints": constraints,
                    "data_scope": data_scope,
                },
                ["query", "selected_object_id"],
            ),
            "output_schema": _schema(
                {"decision_receipt": {"type": "object"}, "read_only": {"const": True}, "data_scope": text}
            ),
        },
        {
            "name": "route_objective",
            "description": "vNext read-only Objective Router: return ALLOW/HOLD/BLOCK route decisions for source-traced capability candidates.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "query": text,
                    "objective": text,
                    "domain": {"type": "string", "default": "mcp_servers"},
                    "data_scope": {
                        "type": "string",
                        "enum": ["sample", "integrated", "mcp_registry", "public_beta_mcp"],
                        "default": "sample",
                    },
                    "limit": {"type": "integer", "default": 10, "minimum": 1},
                    "constraints": constraints,
                },
                ["query", "objective"],
            ),
            "output_schema": _schema(
                {
                    "schema": text,
                    "route_summary": {"type": "object"},
                    "results": {"type": "array"},
                    "read_only": {"const": True},
                    "probe_execution": {"const": False},
                    "gateway_execution": {"const": False},
                }
            ),
        },
        {
            "name": "get_capability_trust",
            "description": "Return one vNext CapabilityTrustCard by capability id without network, probes, or external tool execution.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "capability_id": text,
                    "data_scope": {
                        "type": "string",
                        "enum": ["sample", "integrated", "mcp_registry", "public_beta_mcp"],
                        "default": "sample",
                    },
                },
                ["capability_id"],
            ),
            "output_schema": _schema(
                {
                    "capability_trust_card": {"type": "object"},
                    "found": {"type": "boolean"},
                    "read_only": {"const": True},
                    "probe_execution": {"const": False},
                }
            ),
        },
        {
            "name": "explain_route_decision",
            "description": "Explain one vNext route decision with evidence summary, risk boundary, missing fields, and must-not-claim terms.",
            "read_only": True,
            "input_schema": _schema(
                {
                    "capability_id": text,
                    "objective": optional_text,
                    "data_scope": {
                        "type": "string",
                        "enum": ["sample", "integrated", "mcp_registry", "public_beta_mcp"],
                        "default": "sample",
                    },
                },
                ["capability_id"],
            ),
            "output_schema": _schema(
                {
                    "decision": text,
                    "reason": text,
                    "evidence_summary": {"type": "object"},
                    "risk_boundary": {"type": "object"},
                    "must_not_claim": {"type": "array"},
                    "read_only": {"const": True},
                    "probe_execution": {"const": False},
                }
            ),
        },
    ]

    return {
        "server_name": "ai-objective-index",
        "purpose": "Expose the AI Objective Index core engine through read-only MCP tools over local sample, generated, integrated, curated, public_beta, mcp_registry, or public_beta_mcp data scopes.",
        "read_only": True,
        "default_data_scope": "sample",
        "data_scopes": [
            "sample",
            "generated",
            "integrated",
            "curated",
            "public_beta",
            "mcp_registry",
            "public_beta_mcp",
        ],
        "tools": tools,
        "forbidden_actions": FORBIDDEN_ACTIONS,
    }


def save_mcp_tool_manifest(path: str | Path = "data/generated_mcp_tools_manifest.json") -> Path:
    destination = Path(path)
    if not destination.is_absolute():
        destination = Path.cwd() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(get_mcp_tool_manifest(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def main() -> None:
    path = save_mcp_tool_manifest()
    manifest = get_mcp_tool_manifest()
    print(f"Saved MCP tool manifest: {path}")
    print(f"server_name: {manifest['server_name']}")
    print(f"read_only: {manifest['read_only']}")
    print("tools: " + ", ".join(tool["name"] for tool in manifest["tools"]))


if __name__ == "__main__":
    main()
