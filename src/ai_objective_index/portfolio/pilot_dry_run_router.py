from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_intake_packager import AGENTSEC_PACKET_PATH, DATACAPSULE_PACKET_PATH, QIRA_PACKET_PATH, package_pilot_intake
from .pilot_intake_packet import PilotIntakePacket
from .pilot_vertical_router import PilotVerticalRoute, route_intake_packet, route_to_jsonable


SAMPLE_PACKET_PATHS = {
    "agentsec": AGENTSEC_PACKET_PATH,
    "qira": QIRA_PACKET_PATH,
    "datacapsule": DATACAPSULE_PACKET_PATH,
}
EXPECTED_ROUTES = {"agentsec": "agentsec", "qira": "qira", "datacapsule": "datacapsule"}


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    payload = json.loads(full.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_sample_intake_packets(ensure_samples: bool = True) -> dict[str, PilotIntakePacket]:
    if ensure_samples:
        package_pilot_intake(sample=True)
    packets: dict[str, PilotIntakePacket] = {}
    for vertical, path in SAMPLE_PACKET_PATHS.items():
        payload = _read_json(path)
        if payload:
            packets[vertical] = PilotIntakePacket.model_validate(payload)
    return packets


def route_sample_intake_packets(ensure_samples: bool = True) -> dict[str, PilotVerticalRoute]:
    packets = load_sample_intake_packets(ensure_samples=ensure_samples)
    return {vertical: route_intake_packet(packet) for vertical, packet in packets.items()}


def build_route_trace(routes: dict[str, PilotVerticalRoute]) -> list[dict[str, Any]]:
    trace: list[dict[str, Any]] = []
    for expected, route in routes.items():
        payload = route_to_jsonable(route)
        payload["expected_vertical"] = EXPECTED_ROUTES[expected]
        payload["route_matches_expected"] = route.selected_vertical == EXPECTED_ROUTES[expected]
        trace.append(payload)
    return trace
