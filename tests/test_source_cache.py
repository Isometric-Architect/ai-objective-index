from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from ai_objective_index.crawler.source_cache import SourceCache


def test_source_cache_write_read_list() -> None:
    cache_root = Path("data/generated") / f"source_cache_test_{uuid4().hex}"
    try:
        cache = SourceCache(cache_root)

        record = cache.write_source("https://example.com/docs", "<html>Docs</html>")
        loaded = cache.read_source(record["cache_id"])
        records = cache.list_sources()

        assert loaded["url"] == "https://example.com/docs"
        assert loaded["content"] == "<html>Docs</html>"
        assert len(records) == 1
        assert records[0]["cache_id"] == record["cache_id"]
    finally:
        if cache_root.exists():
            rmtree(cache_root)
