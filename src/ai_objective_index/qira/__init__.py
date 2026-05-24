"""QIRA-Code ReleaseGate MVP.

Local/offline QBCPL-inspired behavior contracts, residual ledgers, patch
receipts, and action-license decisions for AI-generated code changes.
"""

from .models import (
    ActionLicense,
    BehaviorContract,
    PatchCandidate,
    PatchReceipt,
    QiraReleaseGateReport,
    ResidualLedger,
    ValidatorPacket,
)
from .input_packet import QiraTaskPacket
from .packet_loader import build_report_from_packet, build_report_from_packet_file, load_task_packet
from .diff_classifier import ChangedFileClassification, PatchDiffClassificationReport, classify_patch_paths
from .ci_evidence import (
    CiCheckResult,
    CiEvidencePacket,
    CiEvidenceValidationResult,
    apply_ci_evidence_to_packet,
    build_qira6_ci_review,
    validate_ci_evidence,
)
from .packet_generator import QiraPacketGenerationRequest, QiraPacketGenerationResult, generate_packet_from_request
from .releasegate import build_release_gate_report
from .test_command_contract import TestCommandContract, TestCommandRecord, build_test_command_contract

__all__ = [
    "ActionLicense",
    "BehaviorContract",
    "PatchCandidate",
    "PatchReceipt",
    "QiraTaskPacket",
    "QiraPacketGenerationRequest",
    "QiraPacketGenerationResult",
    "QiraReleaseGateReport",
    "CiCheckResult",
    "CiEvidencePacket",
    "CiEvidenceValidationResult",
    "ResidualLedger",
    "ChangedFileClassification",
    "PatchDiffClassificationReport",
    "TestCommandContract",
    "TestCommandRecord",
    "ValidatorPacket",
    "apply_ci_evidence_to_packet",
    "build_qira6_ci_review",
    "build_report_from_packet",
    "build_report_from_packet_file",
    "build_release_gate_report",
    "build_test_command_contract",
    "classify_patch_paths",
    "generate_packet_from_request",
    "load_task_packet",
    "validate_ci_evidence",
]
