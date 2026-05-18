from __future__ import annotations

import re
from collections.abc import Iterable

from .missing_fields import list_missing_fields
from .models import ActionObject, MissingField, SourceTrace


_STOPWORDS = {
    "a",
    "an",
    "and",
    "api",
    "for",
    "in",
    "of",
    "or",
    "the",
    "to",
    "with",
}


def _tokens(value: str) -> set[str]:
    text = re.sub(r"[_/-]+", " ", value.lower())
    return {token for token in re.findall(r"[a-z0-9]+", text) if token not in _STOPWORDS}


def _object_text(action_object: ActionObject) -> str:
    parts = [
        action_object.name,
        action_object.summary,
        str(action_object.object_type),
        " ".join(action_object.capabilities),
        " ".join(action_object.categories),
    ]
    return " ".join(part for part in parts if part)


def _domain_matches(action_object: ActionObject, domain: str | None) -> bool:
    if not domain:
        return True

    normalized = domain.lower()
    object_type = str(action_object.object_type).lower()
    categories = {item.lower() for item in action_object.categories}

    if normalized in {"ai_tools", "mixed_ai_tools"}:
        return True
    if normalized == "ai_apis":
        return "api" in object_type or any("api" in item for item in categories)
    if normalized == "ai_saas":
        return "saas" in object_type or any("saas" in item for item in categories)
    if normalized == "mcp_servers":
        return "mcp" in object_type or any("mcp" in item for item in categories)
    return True


class ObjectiveIndexStore:
    def __init__(self, objects: Iterable[ActionObject], traces: Iterable[SourceTrace]):
        self._objects = {item.object_id: item for item in objects}
        self._traces = list(traces)
        self._trace_by_id = {trace.trace_id: trace for trace in self._traces}
        self._traces_by_object: dict[str, list[SourceTrace]] = {}
        for trace in self._traces:
            self._traces_by_object.setdefault(trace.object_id, []).append(trace)

    def get_object(self, object_id: str) -> ActionObject | None:
        return self._objects.get(object_id)

    def list_objects(self) -> list[ActionObject]:
        return list(self._objects.values())

    def search_objects(
        self, query: str, domain: str | None = None, limit: int = 10
    ) -> list[ActionObject]:
        query_tokens = _tokens(query)
        scored: list[tuple[int, int, ActionObject]] = []

        for index, action_object in enumerate(self._objects.values()):
            if not _domain_matches(action_object, domain):
                continue
            object_tokens = _tokens(_object_text(action_object))
            overlap = len(query_tokens & object_tokens)
            scored.append((overlap, -index, action_object))

        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [item[2] for item in scored[:limit]]

    def get_traces(self, object_id: str, field: str | None = None) -> list[SourceTrace]:
        traces = self._traces_by_object.get(object_id, [])
        if field is None:
            return list(traces)
        return [
            trace
            for trace in traces
            if trace.field == field
            or trace.field.startswith(f"{field}.")
            or field.startswith(f"{trace.field}.")
        ]

    def get_trace_by_id(self, trace_id: str) -> SourceTrace | None:
        return self._trace_by_id.get(trace_id)

    def list_missing_fields(self, object_id: str) -> list[MissingField]:
        action_object = self.get_object(object_id)
        if action_object is None:
            return []
        return list_missing_fields(action_object)
