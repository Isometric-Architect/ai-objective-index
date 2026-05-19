from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_registry_client import fetch_registry_servers, load_raw_registry_fixture, save_raw_registry_payload
from .mcp_registry_evidence_gate import validate_registry_dataset
from .mcp_registry_loader import load_registry_raw, normalize_registry_records
from .mcp_registry_mapper import registry_record_to_action_object, registry_record_to_source_traces
from .real_payload_guard import assert_no_fixture_overwrite, is_fixture_payload


DEFAULT_OUTPUT_DIR = Path("data/registry")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _jsonl_write(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _parse_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return True
    return str(value).strip().lower() not in {"0", "false", "no", "off"}


def export_mcp_registry_intake(
    allow_network: bool = False,
    max_servers: int = 50,
    use_fixture: bool = True,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    raw_path: str | Path | None = None,
    force_fixture: bool = False,
) -> dict[str, Any]:
    destination = _resolve(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []
    fixture_mode = use_fixture
    live_network_used = False

    if allow_network and not use_fixture:
        raw = fetch_registry_servers(max_servers=max_servers, allow_network=True)
        if raw.get("error"):
            warnings.append(str(raw["error"]))
            warnings.append("Falling back to local fixture. See manual download instructions.")
            fixture_mode = True
            raw_payload = load_raw_registry_fixture()
        else:
            live_network_used = bool(raw.get("live_network_used"))
            raw_payload = raw.get("payload", raw)
    elif use_fixture:
        raw_payload = load_raw_registry_fixture()
    else:
        raw_payload = load_registry_raw(
            path=raw_path or destination / "mcp_registry_raw_v0_1.json",
            fallback_fixture=False,
        )
        if not normalize_registry_records(raw_payload, max_servers=max_servers):
            warnings.append("No manual registry raw payload found; falling back to fixture.")
            fixture_mode = True
            raw_payload = load_raw_registry_fixture()
    if not use_fixture and is_fixture_payload(raw_payload):
        fixture_mode = True
        warnings.append("Existing raw payload is fixture data; it will not be treated as real public beta MCP data.")

    raw_wrapper = {
        "generated_at": datetime.now(UTC).isoformat(),
        "fixture_mode": fixture_mode,
        "live_network_used": live_network_used,
        "source": "fixture" if fixture_mode else "official_mcp_registry_api",
        "payload": raw_payload,
    }
    overwrite_guard = assert_no_fixture_overwrite(destination / "mcp_registry_raw_v0_1.json", "fixture" if fixture_mode else "official_mcp_registry_api")
    raw_payload_preserved = False
    if fixture_mode and overwrite_guard["blocked"] and not force_fixture:
        raw_payload_preserved = True
        warnings.append(overwrite_guard["reason"])
    else:
        save_raw_registry_payload(raw_wrapper, destination / "mcp_registry_raw_v0_1.json")

    records = normalize_registry_records(raw_payload, max_servers=max_servers)
    if fixture_mode:
        records = [{**record, "fixture_only": True} for record in records]
    objects = [registry_record_to_action_object(record) for record in records]
    traces = [
        trace
        for record in records
        for trace in registry_record_to_source_traces(record)
    ]
    validation = validate_registry_dataset(objects, traces)
    public_beta_ids = {
        result["object_id"]
        for result in validation["object_results"]
        if result["public_beta_ready"] and not fixture_mode
    }
    public_beta_objects = [item for item in objects if item.object_id in public_beta_ids]
    public_beta_traces = [trace for trace in traces if trace.object_id in public_beta_ids]

    _jsonl_write(
        destination / "mcp_registry_objects_v0_1.jsonl",
        [item.model_dump(mode="json") for item in objects],
    )
    _jsonl_write(
        destination / "mcp_registry_source_traces_v0_1.jsonl",
        [item.model_dump(mode="json") for item in traces],
    )
    (destination / "mcp_registry_validation_results_v0_1.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    public_beta_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": live_network_used,
        "fixture_mode": fixture_mode,
        "supplier_verified": False,
        "object_count": len(objects),
        "trace_count": len(traces),
        "public_beta_ready_count": len(public_beta_objects),
        "objects": [item.model_dump(mode="json") for item in public_beta_objects],
        "source_traces": [item.model_dump(mode="json") for item in public_beta_traces],
        "validation_summary": validation,
        "warnings": warnings
        + (["Fixture mode records are not promoted to public_beta_mcp."] if fixture_mode else []),
    }
    (destination / "mcp_registry_public_beta_index_v0_1.json").write_text(
        json.dumps(public_beta_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "read_only": True,
        "live_network_used": live_network_used,
        "fixture_mode": fixture_mode,
        "object_count": len(objects),
        "trace_count": len(traces),
        "public_beta_ready_count": len(public_beta_objects),
        "validation_summary": validation,
        "warnings": public_beta_payload["warnings"],
        "output_dir": str(destination),
        "raw_payload_preserved": raw_payload_preserved,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export AOI MCP Registry intake data.")
    parser.add_argument("--allow-network", action="store_true", help="Enable read-only GET to the official MCP Registry API.")
    parser.add_argument("--max-servers", type=int, default=50)
    parser.add_argument("--use-fixture", nargs="?", const="true", default="true")
    parser.add_argument("--force-fixture", action="store_true", help="Allow fixture mode to overwrite an existing real/manual raw payload.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    payload = export_mcp_registry_intake(
        allow_network=args.allow_network,
        max_servers=args.max_servers,
        use_fixture=_parse_bool(args.use_fixture),
        output_dir=args.output_dir,
        force_fixture=args.force_fixture,
    )
    print(
        "MCP registry export: "
        f"fixture_mode={payload['fixture_mode']} "
        f"objects={payload['object_count']} "
        f"traces={payload['trace_count']} "
        f"public_beta_ready={payload['public_beta_ready_count']} "
        f"live_network_used={payload['live_network_used']}"
    )


if __name__ == "__main__":
    main()
