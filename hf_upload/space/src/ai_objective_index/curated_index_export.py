from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .curated_loader import load_curated_objects, load_curated_source_traces
from .curated_validator import validate_curated_dataset


DEFAULT_OUTPUT = Path("data/curated/curated_public_beta_index_v0_1.json")
DEFAULT_VALIDATION_OUTPUT = Path("data/curated/curated_validation_results_v0_1.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def export_curated_index(
    input_path: str | Path = "data/curated/curated_objects_v0_1.jsonl",
    traces_path: str | Path = "data/curated/curated_source_traces_v0_1.jsonl",
    output_path: str | Path = DEFAULT_OUTPUT,
    validation_output_path: str | Path = DEFAULT_VALIDATION_OUTPUT,
) -> dict[str, Any]:
    objects = load_curated_objects(input_path)
    traces = load_curated_source_traces(traces_path)
    validation = validate_curated_dataset(objects, traces)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": False,
        "supplier_verified": False,
        "object_count": len(objects),
        "trace_count": len(traces),
        "public_beta_ready_count": validation["public_beta_ready_count"],
        "validation_summary": validation,
        "objects": [item.model_dump(mode="json") for item in objects],
        "source_traces": [item.model_dump(mode="json") for item in traces],
        "known_limits": [
            "curated objects are not supplier verified",
            "manual curation only; no live crawling",
            "public_beta excludes placeholder/fake sample records by default",
        ],
    }
    destination = Path(output_path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    validation_destination = Path(validation_output_path)
    if not validation_destination.is_absolute():
        validation_destination = _repo_root() / validation_destination
    validation_destination.parent.mkdir(parents=True, exist_ok=True)
    validation_destination.write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Export curated AOI public beta index.")
    parser.add_argument("--input", default="data/curated/curated_objects_v0_1.jsonl")
    parser.add_argument("--traces", default="data/curated/curated_source_traces_v0_1.jsonl")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    payload = export_curated_index(args.input, args.traces, args.output)
    print(
        "Curated export: "
        f"objects={payload['object_count']} "
        f"traces={payload['trace_count']} "
        f"public_beta_ready={payload['public_beta_ready_count']}"
    )


if __name__ == "__main__":
    main()
