from __future__ import annotations

from .curated_evidence_gate import evidence_gate_for_public_beta
from .curated_loader import load_curated_objects, load_curated_source_traces
from .generated_loader import load_generated_objects, load_generated_source_traces
from .models import ActionObject, SourceTrace
from .registry_intake.mcp_registry_evidence_gate import evidence_gate_registry_public_beta
from .registry_intake.mcp_registry_loader import load_registry_objects, load_registry_source_traces
from .registry_intake.registry_beta_dataset_builder import (
    load_registry_beta_candidate_objects,
    load_registry_beta_candidate_traces,
)
from .seed_loader import load_sample_index, load_source_traces
from .store import ObjectiveIndexStore


VALID_SCOPES = {
    "sample",
    "generated",
    "integrated",
    "curated",
    "public_beta",
    "mcp_registry",
    "public_beta_mcp",
}


def _normalize_scope(scope: str | None) -> str:
    normalized = (scope or "sample").lower()
    if normalized not in VALID_SCOPES:
        expected = ", ".join(sorted(VALID_SCOPES))
        raise ValueError(f"Unknown data scope: {scope}. Expected one of: {expected}.")
    return normalized


def build_integrated_traces(
    include_sample: bool = True,
    include_generated: bool = True,
    include_curated: bool = False,
    include_mcp_registry: bool = False,
    public_beta_only: bool = False,
    public_beta_mcp_only: bool = False,
) -> list[SourceTrace]:
    traces: list[SourceTrace] = []
    if include_sample:
        traces.extend(load_source_traces())
    if include_generated:
        traces.extend(load_generated_source_traces())
    if include_curated:
        curated_traces = load_curated_source_traces()
        if public_beta_only:
            public_beta_ids = {
                item.object_id
                for item in _public_beta_objects(load_curated_objects(), curated_traces)
            }
            curated_traces = [trace for trace in curated_traces if trace.object_id in public_beta_ids]
        traces.extend(curated_traces)
    if include_mcp_registry:
        registry_traces = (
            load_registry_beta_candidate_traces()
            if public_beta_mcp_only
            else load_registry_source_traces()
        )
        if public_beta_mcp_only and registry_traces:
            traces.extend(registry_traces)
            return traces
        if public_beta_mcp_only:
            public_beta_ids = {
                item.object_id
                for item in _public_beta_mcp_objects(load_registry_objects(), registry_traces)
            }
            registry_traces = [trace for trace in registry_traces if trace.object_id in public_beta_ids]
        traces.extend(registry_traces)
    return traces


def _public_beta_objects(
    objects: list[ActionObject],
    traces: list[SourceTrace],
) -> list[ActionObject]:
    traces_by_object: dict[str, list[SourceTrace]] = {}
    for trace in traces:
        traces_by_object.setdefault(trace.object_id, []).append(trace)
    return [
        action_object
        for action_object in objects
        if evidence_gate_for_public_beta(
            action_object,
            traces_by_object.get(action_object.object_id, []),
        ).get("public_beta_ready")
    ]


def _public_beta_mcp_objects(
    objects: list[ActionObject],
    traces: list[SourceTrace],
) -> list[ActionObject]:
    calibrated_candidates = load_registry_beta_candidate_objects()
    if calibrated_candidates:
        return calibrated_candidates
    traces_by_object: dict[str, list[SourceTrace]] = {}
    for trace in traces:
        traces_by_object.setdefault(trace.object_id, []).append(trace)
    return [
        action_object
        for action_object in objects
        if evidence_gate_registry_public_beta(
            action_object,
            traces_by_object.get(action_object.object_id, []),
        ).get("public_beta_ready")
    ]


def _objects(
    include_sample: bool,
    include_generated: bool,
    include_curated: bool = False,
    include_mcp_registry: bool = False,
    public_beta_only: bool = False,
    public_beta_mcp_only: bool = False,
) -> list[ActionObject]:
    objects: list[ActionObject] = []
    if include_sample:
        objects.extend(load_sample_index())
    if include_generated:
        objects.extend(load_generated_objects())
    if include_curated:
        curated_objects = load_curated_objects()
        if public_beta_only:
            curated_objects = _public_beta_objects(curated_objects, load_curated_source_traces())
        objects.extend(curated_objects)
    if include_mcp_registry:
        registry_objects = (
            load_registry_beta_candidate_objects()
            if public_beta_mcp_only
            else load_registry_objects()
        )
        if public_beta_mcp_only and registry_objects:
            objects.extend(registry_objects)
            return objects
        if public_beta_mcp_only:
            registry_objects = _public_beta_mcp_objects(registry_objects, load_registry_source_traces())
        objects.extend(registry_objects)
    return objects


def build_integrated_store(
    include_sample: bool = True,
    include_generated: bool = True,
    include_curated: bool = False,
    include_mcp_registry: bool = False,
    public_beta_only: bool = False,
    public_beta_mcp_only: bool = False,
) -> ObjectiveIndexStore:
    return ObjectiveIndexStore(
        _objects(
            include_sample=include_sample,
            include_generated=include_generated,
            include_curated=include_curated,
            include_mcp_registry=include_mcp_registry,
            public_beta_only=public_beta_only,
            public_beta_mcp_only=public_beta_mcp_only,
        ),
        build_integrated_traces(
            include_sample=include_sample,
            include_generated=include_generated,
            include_curated=include_curated,
            include_mcp_registry=include_mcp_registry,
            public_beta_only=public_beta_only,
            public_beta_mcp_only=public_beta_mcp_only,
        ),
    )


def get_store_for_scope(scope: str = "sample") -> ObjectiveIndexStore:
    normalized = _normalize_scope(scope)
    return build_integrated_store(
        include_sample=normalized in {"sample", "integrated"},
        include_generated=normalized in {"generated", "integrated"},
        include_curated=normalized in {"curated", "public_beta"},
        include_mcp_registry=normalized in {"mcp_registry", "public_beta_mcp"},
        public_beta_only=normalized == "public_beta",
        public_beta_mcp_only=normalized == "public_beta_mcp",
    )
