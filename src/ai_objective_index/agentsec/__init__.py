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
    AgentSecPolicyGateResult,
    AgentSecPolicyProfile,
    AgentSecScanResult,
    PermissionScope,
    ToolRiskPacket,
)
from .policy_gate import (
    apply_policy_profile,
    build_agentsec2_sample_outputs,
    build_policy_gate_result,
    developer_default_profile,
    read_manifest_set,
    strict_enterprise_profile,
)

__all__ = [
    "AgentSecActionBoundaryReceipt",
    "AgentSecPolicyGateResult",
    "AgentSecPolicyProfile",
    "AgentSecScanResult",
    "PermissionScope",
    "SAMPLE_MANIFEST",
    "ToolRiskPacket",
    "build_action_boundary_receipt",
    "build_agentsec1_sample_outputs",
    "build_agentsec2_sample_outputs",
    "build_policy_gate_result",
    "apply_policy_profile",
    "developer_default_profile",
    "read_manifest_set",
    "scan_manifest_payload",
    "scan_manifest_path",
    "strict_enterprise_profile",
]
