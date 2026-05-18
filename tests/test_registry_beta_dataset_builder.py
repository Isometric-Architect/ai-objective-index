from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from ai_objective_index.registry_intake.registry_beta_dataset_builder import build_registry_beta_dataset


def test_registry_beta_dataset_builder_writes_candidates() -> None:
    workspace_tmp = Path("data/generated/test_registry_beta_dataset_builder")
    workspace_tmp.mkdir(parents=True, exist_ok=True)
    objects_path = workspace_tmp / "objects.jsonl"
    traces_path = workspace_tmp / "traces.jsonl"
    output_dir = workspace_tmp / "registry"
    obj = {
        "object_id": "mcp-registry-example-beta-0-1-0",
        "name": "io.github.example/beta",
        "object_type": "MCPServer",
        "summary": "Registry metadata for a browser automation MCP server.",
        "official_url": "https://registry.modelcontextprotocol.io/v0.1/servers/io.github.example/beta/versions/0.1.0",
        "source_urls": ["https://registry.modelcontextprotocol.io/v0.1/servers/io.github.example/beta/versions/0.1.0"],
        "capabilities": ["mcp_server", "browser_automation"],
        "categories": ["mcp_server", "mcp_registry"],
        "pricing": {},
        "policies": {"registry_source": "official_mcp_registry_metadata"},
        "docs": {"repository_url": "https://github.com/example/beta"},
        "status": "EXTRACTED_UNVERIFIED",
        "confidence": 0.65,
        "missing_fields": [],
        "package_metadata": [{"registry": "npm", "name": "@example/beta"}],
    }
    trace = {
        "trace_id": "trace-mcp-registry-example-beta-0-1-0-name",
        "object_id": "mcp-registry-example-beta-0-1-0",
        "field": "name",
        "source_url": "https://registry.modelcontextprotocol.io/v0.1/servers/io.github.example/beta/versions/0.1.0",
        "source_title": "Official MCP Registry record",
        "source_snippet": "io.github.example/beta",
        "retrieved_at": datetime.now(UTC).isoformat(),
        "confidence": 0.75,
        "source_rank": "A",
    }
    objects_path.write_text(json.dumps(obj) + "\n", encoding="utf-8")
    traces_path.write_text(json.dumps(trace) + "\n", encoding="utf-8")

    result = build_registry_beta_dataset(objects_path=objects_path, traces_path=traces_path, output_dir=output_dir)

    assert result["live_network_used"] is False
    assert result["beta_candidate_count"] == 1
    candidates_path = output_dir / "mcp_registry_beta_candidates_v0_1.jsonl"
    dataset_path = output_dir / "mcp_registry_public_beta_mcp_dataset_v0_1.json"
    assert candidates_path.exists()
    assert dataset_path.exists()
    candidate = json.loads(candidates_path.read_text(encoding="utf-8").splitlines()[0])
    assert candidate["verified"] is False
    assert candidate["action_ready"] is False
    assert candidate["status"] == "EXTRACTED_UNVERIFIED"
    assert candidate["display_status"] == "REGISTRY_METADATA_CANDIDATE"
