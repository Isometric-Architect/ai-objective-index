from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .input_packet import QiraTaskPacket, packet_to_contract_and_patch
from .models import BehaviorContract, PatchCandidate
from .releasegate import build_release_gate_report


class QiraPacketError(ValueError):
    """Raised when a local QIRA packet cannot be loaded safely."""


def load_task_packet(path: str | Path) -> QiraTaskPacket:
    source = Path(path)
    if not source.exists() or not source.is_file():
        raise QiraPacketError(f"QIRA task packet not found: {source}")
    if source.suffix.lower() != ".json":
        raise QiraPacketError("QIRA task packet must be a JSON file.")
    if source.stat().st_size > 1_000_000:
        raise QiraPacketError("QIRA task packet is too large for local MVP intake.")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise QiraPacketError(f"Invalid JSON task packet: {exc}") from exc
    try:
        return QiraTaskPacket.model_validate(payload)
    except ValidationError as exc:
        raise QiraPacketError(f"Invalid QIRA task packet: {exc}") from exc


def build_report_from_packet(packet: QiraTaskPacket):
    contract_payload, patch_payload = packet_to_contract_and_patch(packet)
    contract = BehaviorContract(**contract_payload)
    patch = PatchCandidate(**patch_payload)
    return build_release_gate_report(contract, patch)


def build_report_from_packet_file(path: str | Path):
    return build_report_from_packet(load_task_packet(path))
