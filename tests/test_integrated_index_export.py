import json
from pathlib import Path
from shutil import rmtree
from uuid import uuid4

from ai_objective_index.integrated_index_export import export_integrated_index


def test_integrated_index_export_writes_json() -> None:
    output_dir = Path("data/generated") / f"test_export_{uuid4().hex}"
    try:
        result = export_integrated_index(scope="integrated", output_dir=output_dir)
        index_path = Path(result["index_path"])
        trace_path = Path(result["source_trace_path"])

        payload = json.loads(index_path.read_text(encoding="utf-8"))
        trace_payload = json.loads(trace_path.read_text(encoding="utf-8"))

        assert payload["object_count"] > 0
        assert payload["trace_count"] > 0
        assert payload["scope"] == "integrated"
        assert payload["objects"]
        assert trace_payload["source_traces"]
    finally:
        if output_dir.exists():
            rmtree(output_dir)

