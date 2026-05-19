from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class SourceCache:
    def __init__(self, root: str | Path = "data/source_cache") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def cache_id_for_url(url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

    def _metadata_path(self, cache_id: str) -> Path:
        return self.root / f"{cache_id}.json"

    def _content_path(self, cache_id: str) -> Path:
        return self.root / f"{cache_id}.content"

    def write_source(
        self,
        url: str,
        content: str,
        content_type: str = "text/html",
        fetched_at: str | datetime | None = None,
    ) -> dict[str, Any]:
        cache_id = self.cache_id_for_url(url)
        timestamp = fetched_at or datetime.now(UTC)
        if isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        metadata = {
            "url": url,
            "content_type": content_type,
            "fetched_at": timestamp,
            "cache_id": cache_id,
        }
        self._content_path(cache_id).write_text(content, encoding="utf-8")
        self._metadata_path(cache_id).write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return metadata

    def read_source(self, cache_id: str) -> dict[str, Any]:
        metadata = json.loads(self._metadata_path(cache_id).read_text(encoding="utf-8"))
        content = self._content_path(cache_id).read_text(encoding="utf-8")
        return {**metadata, "content": content}

    def list_sources(self) -> list[dict[str, Any]]:
        records = []
        for metadata_path in sorted(self.root.glob("*.json")):
            records.append(json.loads(metadata_path.read_text(encoding="utf-8")))
        return records

