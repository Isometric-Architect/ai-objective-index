"""AgentSec Gate local metadata MVP.

AgentSec-1 scans MCP/tool manifests as local data and emits conservative risk
packets. It does not execute tools, call live MCP servers, contact external
services, certify security, or authorize real-world actions.
"""

from .manifest_scanner import (
    SAMPLE_MANIFEST,
    build_action_boundary_receipt,
    build_agentsec1_sample_outputs,
    scan_manifest_payload,
    scan_manifest_path,
)
from .models import (
    AgentSecActionBoundaryReceipt,
    AgentSecScanResult,
    PermissionScope,
    ToolRiskPacket,
)

__all__ = [
    "AgentSecActionBoundaryReceipt",
    "AgentSecScanResult",
    "PermissionScope",
    "SAMPLE_MANIFEST",
    "ToolRiskPacket",
    "build_action_boundary_receipt",
    "build_agentsec1_sample_outputs",
    "scan_manifest_payload",
    "scan_manifest_path",
]
