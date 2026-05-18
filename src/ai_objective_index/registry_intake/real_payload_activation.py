from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .live_registry_run import FALLBACK_MESSAGE, run_live_registry_intake
from .mcp_registry_export import export_mcp_registry_intake
from .real_payload_guard import detect_payload_mode, summarize_payload_path
from .registry_beta_dataset_builder import build_registry_beta_dataset


DEFAULT_RAW_PATH = Path("data/registry/mcp_registry_raw_v0_1.json")
DEFAULT_OUTPUT = Path("data/registry/real_payload_activation_result_v0_1.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _process_existing_raw(raw_path: Path, max_servers: int) -> dict[str, Any]:
    export = export_mcp_registry_intake(
        allow_network=False,
        max_servers=max_servers,
        use_fixture=False,
        output_dir=raw_path.parent,
        raw_path=raw_path,
    )
    beta = build_registry_beta_dataset(output_dir=raw_path.parent)
    return {
        "export": export,
        "beta": beta,
        "object_count": export.get("object_count", 0),
        "trace_count": export.get("trace_count", 0),
        "public_beta_mcp_count": beta.get("beta_candidate_count", 0),
    }


def _alternate_root_raw() -> Path:
    return _repo_root() / "mcp_registry_raw_v0_1.json"


def activate_real_payload(
    try_live: bool = False,
    use_existing_raw: bool = False,
    manual_raw: str | Path | None = None,
    max_servers: int = 50,
    force_fixture: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT,
    raw_target: str | Path = DEFAULT_RAW_PATH,
) -> dict[str, Any]:
    raw_path = _resolve(raw_target)
    errors: list[str] = []
    warnings: list[str] = []
    live_network_used = False
    activated = False
    mode = "offline"

    if try_live:
        mode = "live_try"
        live_result = run_live_registry_intake(allow_network=True, max_servers=max_servers)
        live_network_used = bool(live_result.get("live_network_used"))
        if live_result.get("success"):
            mode = "live_raw"
            activated = True
        else:
            errors.extend(str(item) for item in live_result.get("errors", []))
            warnings.append(FALLBACK_MESSAGE)

    if use_existing_raw and manual_raw is None and not activated and raw_path == _resolve(DEFAULT_RAW_PATH):
        current_mode = detect_payload_mode(raw_path)
        alternate = _alternate_root_raw()
        alternate_mode = detect_payload_mode(alternate)
        if current_mode not in {"manual_raw", "live_raw"} and alternate_mode in {"manual_raw", "live_raw"}:
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(alternate, raw_path)
            warnings.append(f"Activated root-level manual raw payload from {alternate}.")

    if manual_raw is not None and not activated:
        mode = "manual_raw"
        source = _resolve(manual_raw)
        if not source.exists():
            errors.append(f"Manual raw file not found: {source}")
        else:
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() != raw_path.resolve():
                shutil.copyfile(source, raw_path)
            use_existing_raw = True

    payload_mode = detect_payload_mode(raw_path)
    payload_summary = summarize_payload_path(raw_path)

    if use_existing_raw and not activated:
        mode = payload_mode
        if payload_mode in {"manual_raw", "live_raw"}:
            processed = _process_existing_raw(raw_path, max_servers=max_servers)
            activated = True
            payload_summary = summarize_payload_path(raw_path)
        elif payload_mode == "fixture":
            processed = {}
            warnings.append("Existing raw payload is fixture data; not activating public_beta_mcp.")
        elif payload_mode == "missing":
            processed = {}
            warnings.append(FALLBACK_MESSAGE)
        else:
            processed = {}
            warnings.append("Existing raw payload could not be recognized as Official MCP Registry JSON.")
    else:
        processed = {}

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "raw_payload_path": str(raw_path),
        "payload_mode": payload_mode,
        "object_count_raw": payload_summary.get("record_count", 0),
        "activated": activated,
        "live_network_used": live_network_used,
        "errors": errors,
        "warnings": warnings,
        "next_action": (
            "Run registry_reprocess_all and review public_beta_mcp candidates."
            if activated
            else FALLBACK_MESSAGE
        ),
        "processed": processed,
        "read_only": True,
        "arbitrary_scraping_used": False,
        "link_following_used": False,
        "credentials_used": False,
    }
    _write_json(_resolve(output_path), result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Activate real/manual Official MCP Registry raw payload.")
    parser.add_argument("--try-live", action="store_true", help="Attempt explicit read-only live registry intake.")
    parser.add_argument("--use-existing-raw", action="store_true", help="Process data/registry/mcp_registry_raw_v0_1.json if it is real/manual raw.")
    parser.add_argument("--manual-raw", default=None, help="Path to a manually downloaded registry JSON payload.")
    parser.add_argument("--max-servers", type=int, default=50)
    parser.add_argument("--force-fixture", action="store_true")
    args = parser.parse_args()
    result = activate_real_payload(
        try_live=args.try_live,
        use_existing_raw=args.use_existing_raw,
        manual_raw=args.manual_raw,
        max_servers=args.max_servers,
        force_fixture=args.force_fixture,
    )
    print(
        "real_payload_activation: "
        f"mode={result['mode']} "
        f"payload_mode={result['payload_mode']} "
        f"raw_count={result['object_count_raw']} "
        f"activated={result['activated']} "
        f"live_network_used={result['live_network_used']}"
    )
    if result.get("warnings"):
        print("warnings: " + " | ".join(str(item) for item in result["warnings"]))
    if result.get("errors"):
        print("errors: " + " | ".join(str(item) for item in result["errors"]))


if __name__ == "__main__":
    main()
