from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .integrated_store import VALID_SCOPES, get_store_for_scope


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _path(path: str | Path) -> Path:
    destination = Path(path)
    if destination.is_absolute():
        return destination
    return _repo_root() / destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def export_integrated_index(
    scope: str = "integrated",
    output_dir: str | Path = "data/generated",
) -> dict[str, Any]:
    store = get_store_for_scope(scope)
    objects = store.list_objects()
    traces = build_traces_from_store(store)
    generated_at = datetime.now(UTC).isoformat()
    status_counts = dict(Counter(str(item.status) for item in objects))
    payload = {
        "version": "0.2-package-6c",
        "generated_at": generated_at,
        "scope": scope,
        "object_count": len(objects),
        "trace_count": len(traces),
        "status_counts": status_counts,
        "objects": [item.model_dump(mode="json") for item in objects],
    }
    trace_payload = {
        "version": "0.2-package-6c",
        "generated_at": generated_at,
        "scope": scope,
        "object_count": len(objects),
        "trace_count": len(traces),
        "source_traces": [item.model_dump(mode="json") for item in traces],
    }
    destination = _path(output_dir)
    index_path = _write_json(destination / "integrated_index_v0_2.json", payload)
    trace_path = _write_json(destination / "integrated_source_traces_v0_2.json", trace_payload)
    return {
        "scope": scope,
        "object_count": len(objects),
        "trace_count": len(traces),
        "status_counts": status_counts,
        "index_path": str(index_path),
        "source_trace_path": str(trace_path),
    }


def build_traces_from_store(store) -> list[Any]:
    traces = []
    seen = set()
    for action_object in store.list_objects():
        for trace in store.get_traces(action_object.object_id):
            if trace.trace_id in seen:
                continue
            seen.add(trace.trace_id)
            traces.append(trace)
    return traces


def main() -> None:
    parser = argparse.ArgumentParser(description="Export AOI integrated generated/sample index.")
    parser.add_argument("--scope", choices=sorted(VALID_SCOPES), default="integrated")
    parser.add_argument("--output-dir", default="data/generated")
    args = parser.parse_args()
    result = export_integrated_index(scope=args.scope, output_dir=args.output_dir)
    print("Integrated index export complete")
    print(f"scope: {result['scope']}")
    print(f"object_count: {result['object_count']}")
    print(f"trace_count: {result['trace_count']}")
    print(f"wrote: {result['index_path']}")
    print(f"wrote: {result['source_trace_path']}")


if __name__ == "__main__":
    main()

