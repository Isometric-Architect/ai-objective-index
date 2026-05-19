from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

from ai_objective_index.models import SourceRank, SourceTrace


def find_snippet(text: str, keyword: str, window: int = 160) -> str:
    if not text:
        return ""
    lowered = text.lower()
    target = keyword.lower()
    index = lowered.find(target)
    if index < 0:
        return text[:window].strip()
    start = max(0, index - window // 2)
    end = min(len(text), index + len(keyword) + window // 2)
    return text[start:end].strip()


def _trace_id(object_id: str, field: str, source_url: str) -> str:
    digest = hashlib.sha256(f"{object_id}|{field}|{source_url}".encode("utf-8")).hexdigest()[:12]
    return f"trace-{digest}"


def make_trace(
    object_id: str,
    field: str,
    value: Any,
    source_url: str,
    source_title: str | None = None,
    source_text: str | None = None,
    confidence: float = 0.5,
    source_rank: SourceRank | str = SourceRank.UNKNOWN,
) -> SourceTrace:
    keyword = str(value) if value not in (None, "", [], {}) else field.split(".")[-1]
    snippet = find_snippet(source_text or "", keyword) if source_text else str(value)
    return SourceTrace(
        trace_id=_trace_id(object_id, field, source_url),
        object_id=object_id,
        field=field,
        source_url=source_url,
        source_title=source_title or source_url,
        source_snippet=snippet,
        retrieved_at=datetime.now(UTC).isoformat(),
        confidence=confidence,
        source_rank=source_rank,
    )


def map_field_to_trace(
    object_id: str,
    field: str,
    value: Any,
    source_doc: dict[str, Any],
    confidence: float = 0.5,
    source_rank: SourceRank | str = SourceRank.UNKNOWN,
) -> SourceTrace:
    return make_trace(
        object_id=object_id,
        field=field,
        value=value,
        source_url=source_doc.get("url", ""),
        source_title=source_doc.get("title") or source_doc.get("url", ""),
        source_text=source_doc.get("text", ""),
        confidence=confidence,
        source_rank=source_rank,
    )

