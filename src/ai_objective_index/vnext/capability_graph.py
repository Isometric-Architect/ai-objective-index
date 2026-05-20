from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


NodeType = Literal[
    "Objective",
    "Capability",
    "Tool",
    "MCPServer",
    "Agent",
    "Dataset",
    "Verifier",
    "Benchmark",
    "Provider",
    "FailureMode",
    "ExecutionReceipt",
    "RiskBoundary",
]

EdgeType = Literal[
    "supports",
    "requires",
    "verified_by",
    "fails_under",
    "blocked_by",
    "delegates_to",
    "substitutes_for",
    "composed_with",
    "version_of",
]


class CapabilityGraphNode(BaseModel):
    model_config = ConfigDict(extra="allow")

    node_id: str
    node_type: NodeType
    label: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapabilityGraphEdge(BaseModel):
    model_config = ConfigDict(extra="allow")

    source: str
    target: str
    edge_type: EdgeType
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapabilityGraph(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="aoi.vnext.capability_graph.v0_3", alias="schema")
    nodes: list[CapabilityGraphNode] = Field(default_factory=list)
    edges: list[CapabilityGraphEdge] = Field(default_factory=list)
