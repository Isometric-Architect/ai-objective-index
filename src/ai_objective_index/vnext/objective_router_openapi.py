from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .objective_router_models import ObjectiveRouteRequest, ObjectiveRouteResponse
from .execution_receipt_loop import ExecutionReceiptSubmission, ExecutionReceiptValidationResult, CapabilityReceiptMemory, ObjectiveReceiptSummary, ReceiptRouteOverlay
from .probe_card import CapabilityProbeMemory as CapabilityProbeMemoryVNext
from .probe_card import ProbePlan, ProbeReceipt, ProbeRouteOverlay


OPENAPI_PATH = Path("api") / "vnext" / "objective_router_openapi.json"
AUDIT_PATH = Path("public_launch") / "wave5" / "OBJECTIVE_ROUTER_OPENAPI_AUDIT.json"


def build_objective_router_openapi() -> dict:
    request_schema = ObjectiveRouteRequest.model_json_schema()
    response_schema = ObjectiveRouteResponse.model_json_schema()
    receipt_schema = ExecutionReceiptSubmission.model_json_schema()
    receipt_validation_schema = ExecutionReceiptValidationResult.model_json_schema()
    memory_schema = CapabilityReceiptMemory.model_json_schema()
    objective_summary_schema = ObjectiveReceiptSummary.model_json_schema()
    overlay_schema = ReceiptRouteOverlay.model_json_schema()
    probe_plan_schema = ProbePlan.model_json_schema()
    probe_receipt_schema = ProbeReceipt.model_json_schema()
    probe_memory_schema = CapabilityProbeMemoryVNext.model_json_schema()
    probe_overlay_schema = ProbeRouteOverlay.model_json_schema()
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
            "/v1/execution-receipts": {
                "post": {
                    "summary": "Submit a local execution receipt",
                    "operationId": "submitExecutionReceipt",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": receipt_schema}},
                    },
                    "responses": {
                        "200": {
                            "description": "Receipt validation result and optional local store result",
                            "content": {"application/json": {"schema": receipt_validation_schema}},
                        }
                    },
                }
            },
            "/v1/execution-receipts/{receipt_id}": {
                "get": {
                    "summary": "Fetch a local execution receipt",
                    "operationId": "getExecutionReceipt",
                    "parameters": [
                        {"name": "receipt_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Stored receipt or stable not_found result"}},
                }
            },
            "/v1/capabilities/{capability_id}/receipt-memory": {
                "get": {
                    "summary": "Fetch local receipt memory for one capability",
                    "operationId": "getCapabilityReceiptMemory",
                    "parameters": [
                        {"name": "capability_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Capability receipt memory", "content": {"application/json": {"schema": memory_schema}}}},
                }
            },
            "/v1/objectives/{objective_id}/receipt-summary": {
                "get": {
                    "summary": "Fetch local receipt summary for one objective",
                    "operationId": "getObjectiveReceiptSummary",
                    "parameters": [
                        {"name": "objective_id", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {"200": {"description": "Objective receipt summary", "content": {"application/json": {"schema": objective_summary_schema}}}},
                }
            },
            "/v1/objectives/route-with-receipts": {
                "post": {
                    "summary": "Route an objective and overlay local receipt memory",
                    "operationId": "routeObjectiveWithReceipts",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": request_schema}},
                    },
                    "responses": {"200": {"description": "Objective route response with receipt overlay", "content": {"application/json": {"schema": overlay_schema}}}},
                }
            },
            "/v1/execution-receipts/status": {
                "get": {
                    "summary": "Execution receipt loop status and boundaries",
                    "operationId": "executionReceiptStatus",
                    "responses": {"200": {"description": "Read-only local receipt status"}},
                }
            },
            "/v1/probes/plan": {
                "post": {
                    "summary": "Plan local metadata probes before use",
                    "operationId": "planProbeBeforeUse",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": request_schema}}},
                    "responses": {"200": {"description": "Probe plan", "content": {"application/json": {"schema": probe_plan_schema}}}},
                }
            },
            "/v1/probes/run-local": {
                "post": {
                    "summary": "Run a local-only probe plan",
                    "operationId": "runLocalProbePlan",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": probe_plan_schema}}},
                    "responses": {"200": {"description": "Probe receipt", "content": {"application/json": {"schema": probe_receipt_schema}}}},
                }
            },
            "/v1/probes/{receipt_id}": {
                "get": {
                    "summary": "Fetch one local probe receipt",
                    "operationId": "getProbeReceipt",
                    "parameters": [{"name": "receipt_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Stored probe receipt or stable not_found result"}},
                }
            },
            "/v1/capabilities/{capability_id}/probe-memory": {
                "get": {
                    "summary": "Fetch local probe memory for one capability",
                    "operationId": "getCapabilityProbeMemory",
                    "parameters": [{"name": "capability_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {"200": {"description": "Capability probe memory", "content": {"application/json": {"schema": probe_memory_schema}}}},
                }
            },
            "/v1/objectives/route-with-probes": {
                "post": {
                    "summary": "Route an objective with local probe overlay",
                    "operationId": "routeObjectiveWithProbes",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": request_schema}}},
                    "responses": {"200": {"description": "Objective route response with probe overlay", "content": {"application/json": {"schema": probe_overlay_schema}}}},
                }
            },
            "/v1/probes/status": {
                "get": {
                    "summary": "Probe layer status and boundaries",
                    "operationId": "probeStatus",
                    "responses": {"200": {"description": "Local-only probe status"}},
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
                "local_probe_only": True,
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
