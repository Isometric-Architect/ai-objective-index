from pathlib import Path


def test_aoi_030a2_recovery_assets_exist():
    required = [
        "src/ai_objective_index/aoi_030a2_marker_sync.py",
        "src/ai_objective_index/aoi_030a2_build_verify.py",
        "src/ai_objective_index/aoi_030a2_pypi_upload_gate.py",
        "src/ai_objective_index/aoi_030a2_pypi_verify.py",
        "src/ai_objective_index/aoi_mcp_registry_recovery_gate.py",
        "src/ai_objective_index/aoi_mcp_registry_recovery_publish.py",
        "src/ai_objective_index/aoi_mcp_registry_recovery_reconcile.py",
        "docs/aoi_030a2_mcp_registry_recovery.md",
        "docs/aoi_pypi_marker_sync.md",
        "docs/aoi_mcp_registry_publish_recovery.md",
        "public_launch/aoi_030a2_registry_recovery/AOI_030A2_MARKER_SYNC_RESULT.json",
        "public_launch/aoi_030a2_registry_recovery/AOI_030A2_BUILD_VERIFY_RESULT.json",
        "public_launch/aoi_030a2_registry_recovery/AOI_030A2_PYPI_UPLOAD_RESULT.json",
        "public_launch/aoi_030a2_registry_recovery/AOI_030A2_PYPI_VERIFY_RESULT.json",
        "public_launch/aoi_030a2_registry_recovery/AOI_MCP_REGISTRY_RECOVERY_GATE_RESULT.json",
        "public_launch/aoi_030a2_registry_recovery/AOI_MCP_REGISTRY_RECOVERY_PUBLISH_RESULT.json",
        "public_launch/aoi_030a2_registry_recovery/AOI_MCP_REGISTRY_RECOVERY_RECONCILE_RESULT.json",
    ]

    missing = [path for path in required if not Path(path).exists()]

    assert not missing
