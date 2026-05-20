from ai_objective_index.vnext import CapabilityGraph, CapabilityGraphEdge, CapabilityGraphNode


def test_vnext_capability_graph_accepts_allowed_node_and_edge_types():
    graph = CapabilityGraph(
        nodes=[
            CapabilityGraphNode(node_id="obj-1", node_type="Objective", label="Release audit"),
            CapabilityGraphNode(node_id="cap-1", node_type="Capability", label="twine check"),
        ],
        edges=[
            CapabilityGraphEdge(source="cap-1", target="obj-1", edge_type="supports"),
        ],
    )

    payload = graph.model_dump(by_alias=True)
    assert payload["schema"] == "aoi.vnext.capability_graph.v0_3"
    assert payload["edges"][0]["edge_type"] == "supports"
