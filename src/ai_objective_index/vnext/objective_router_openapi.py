from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .objective_router_models import ObjectiveRouteRequest, ObjectiveRouteResponse


OPENAPI_PATH = Path("api") / "vnext" / "objective_router_openapi.json"
AUDIT_PATH = Path("public_launch") / "wave5" / "OBJECTIVE_ROUTER_OPENAPI_AUDIT.json"


def build_objective_router_openapi() -> dict:
    request_schema = ObjectiveRouteRequest.model_json_schema()
    response_schema = ObjectiveRouteResponse.model_json_schema()
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "AI Objective Index vNext Objective Router API",
            "version": "0.1",
            "description": "Read-only objective-to-capability route decisions. Not verification, security certification, or quality guarantee.",
        },
        "paths": {
            "/v1/objectives/route": {
                "post": {
                    "summary": "Route an objective to source-traced capability candidates",
                    "operationId": "routeObjective",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": request_schema}},
                    },
                    "responses": {
                        "200": {
                            "description": "Objective route response",
                            "content": {"application/json": {"schema": response_schema}},
                        }
                    },
                }
            },
            "/v1/objectives/trust-report": {
                "post": {
                    "summary": "Return the full read-only capability trust report",
                    "operationId": "objectiveTrustReport",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": request_schema}},
                    },
                    "responses": {"200": {"description": "Objective route response"}},
                }
            },
            "/v1/capabilities/{capability_id}/trust": {
                "get": {
                    "summary": "Fetch one capability trust card",
                    "operationId": "getCapabilityTrust",
                    "parameters": [
                        {"name": "capability_id", "in": "path", "required": True, "schema": {"type": "string"}},
                        {"name": "data_scope", "in": "query", "required": False, "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "Capability trust card or stable not_found result"}},
                }
            },
            "/v1/objectives/router/status": {
                "get": {
                    "summary": "Objective Router safety/status metadata",
                    "operationId": "objectiveRouterStatus",
                    "responses": {"200": {"description": "Read-only router status"}},
                }
            },
        },
    }


def save_objective_router_openapi(path: Path = OPENAPI_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_objective_router_openapi()
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(UTC).isoformat(),
                "openapi_path": str(path),
                "paths": sorted(payload["paths"]),
                "read_only": True,
                "probe_execution": False,
                "gateway_execution": False,
                "external_fetch": False,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = save_objective_router_openapi()
    print(f"Saved Objective Router OpenAPI: {path}")


if __name__ == "__main__":
    main()
