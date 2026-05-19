from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.beta_readiness import write_beta_readiness_report
from ai_objective_index.datascope_qa import run_datascope_qa, save_datascope_qa_results

from .mcp_registry_client import DEFAULT_BASE_URL, fetch_registry_servers, save_raw_registry_payload
from .mcp_registry_eval import run_mcp_registry_eval, save_mcp_registry_eval
from .mcp_registry_export import export_mcp_registry_intake
from .mcp_registry_loader import load_registry_objects, load_registry_raw, load_registry_source_traces
from .mcp_registry_report_generator import write_mcp_registry_report
from .registry_live_validation import (
    summarize_live_registry_run,
    validate_live_objects,
    validate_live_payload_shape,
)
from .registry_run_receipt import build_registry_run_receipt, write_registry_run_receipt


DEFAULT_OUTPUT_DIR = Path("data/registry")
ENDPOINT = "/v0.1/servers?limit={limit}"
FALLBACK_MESSAGE = "Download GET /v0.1/servers JSON and save as data/registry/mcp_registry_raw_v0_1.json."


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_fallback_status(
    output_dir: Path,
    mode: str,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
) -> Path:
    payload = {
        "mode": mode,
        "live_network_used": False,
        "manual_fallback_required": True,
        "fallback_step": FALLBACK_MESSAGE,
        "errors": errors or [],
        "warnings": warnings or [],
        "arbitrary_scraping_used": False,
        "link_following_used": False,
        "credentials_used": False,
    }
    destination = output_dir / "mcp_registry_manual_fallback_status_v0_1.json"
    _write_json(destination, payload)
    return destination


def _run_downstream(output_dir: Path, max_servers: int, mode: str) -> dict[str, Any]:
    export = export_mcp_registry_intake(
        allow_network=False,
        max_servers=max_servers,
        use_fixture=False,
        output_dir=output_dir,
        raw_path=output_dir / "mcp_registry_raw_v0_1.json",
    )
    eval_result = run_mcp_registry_eval()
    save_mcp_registry_eval(eval_result)
    report_path = write_mcp_registry_report()
    try:
        save_datascope_qa_results(run_datascope_qa())
        write_beta_readiness_report()
    except Exception as exc:  # pragma: no cover - defensive local report refresh.
        export.setdefault("warnings", []).append(f"Data-scope/beta readiness refresh skipped: {exc}")
    objects = load_registry_objects(output_dir / "mcp_registry_objects_v0_1.jsonl")
    traces = load_registry_source_traces(output_dir / "mcp_registry_source_traces_v0_1.jsonl")
    raw = load_registry_raw(output_dir / "mcp_registry_raw_v0_1.json", fallback_fixture=False)
    payload_validation = validate_live_payload_shape(raw, max_servers=max_servers)
    object_validation = validate_live_objects(
        objects,
        traces,
        max_servers=max_servers,
        live_network_used=mode == "live_registry",
    )
    return {
        "export": export,
        "eval": eval_result,
        "report_path": str(report_path),
        "payload_validation": payload_validation,
        "object_validation": object_validation,
    }


def run_live_registry_intake(
    allow_network: bool = False,
    max_servers: int = 50,
    base_url: str = DEFAULT_BASE_URL,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    use_manual_raw_if_present: bool = True,
    skip_if_no_network: bool = False,
) -> dict[str, Any]:
    destination = _resolve(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    raw_path = destination / "mcp_registry_raw_v0_1.json"
    endpoint = ENDPOINT.format(limit=max_servers)
    errors: list[str] = []
    warnings: list[str] = []
    mode = "offline"
    live_network_used = False

    if allow_network:
        mode = "live_registry"
        response = fetch_registry_servers(
            base_url=base_url,
            max_servers=max_servers,
            allow_network=True,
        )
        if response.get("error"):
            errors.append(str(response["error"]))
            fallback_path = _write_fallback_status(destination, mode, errors=errors, warnings=[FALLBACK_MESSAGE])
            receipt = build_registry_run_receipt(
                mode=mode,
                allow_network=True,
                base_url=base_url,
                endpoint=endpoint,
                max_servers=max_servers,
                raw_payload_path=str(raw_path),
                live_network_used=False,
                errors=errors,
                warnings=[FALLBACK_MESSAGE],
                next_action=FALLBACK_MESSAGE,
            )
            receipt_path = write_registry_run_receipt(receipt, destination / "mcp_registry_live_run_receipt_v0_1.json")
            summary = {
                "mode": mode,
                "live_network_used": False,
                "success": False,
                "fallback_status_path": str(fallback_path),
                "receipt_path": str(receipt_path),
                "errors": errors,
                "warnings": [FALLBACK_MESSAGE],
                "object_count": 0,
                "trace_count": 0,
                "public_beta_ready_count": 0,
            }
            _write_json(destination / "mcp_registry_live_summary_v0_1.json", summary)
            return summary
        live_network_used = bool(response.get("live_network_used"))
        raw_wrapper = {
            "source": "official_mcp_registry_api",
            "fixture_mode": False,
            "live_network_used": live_network_used,
            "base_url": base_url,
            "endpoint": endpoint,
            "payload": response.get("payload", response),
        }
        save_raw_registry_payload(raw_wrapper, raw_path)
    elif use_manual_raw_if_present and raw_path.exists():
        mode = "manual_raw"
        warnings.append("Processed existing local registry raw payload without network.")
    else:
        if skip_if_no_network:
            warnings.append("Skipped live registry run because allow_network is false.")
        fallback_path = _write_fallback_status(destination, mode, warnings=[FALLBACK_MESSAGE, *warnings])
        receipt = build_registry_run_receipt(
            mode=mode,
            allow_network=False,
            base_url=base_url,
            endpoint=endpoint,
            max_servers=max_servers,
            raw_payload_path=str(raw_path),
            live_network_used=False,
            warnings=[FALLBACK_MESSAGE, *warnings],
            next_action=FALLBACK_MESSAGE,
        )
        receipt_path = write_registry_run_receipt(receipt, destination / "mcp_registry_live_run_receipt_v0_1.json")
        summary = {
            "mode": mode,
            "live_network_used": False,
            "success": False,
            "fallback_status_path": str(fallback_path),
            "receipt_path": str(receipt_path),
            "errors": [],
            "warnings": [FALLBACK_MESSAGE, *warnings],
            "object_count": 0,
            "trace_count": 0,
            "public_beta_ready_count": 0,
        }
        _write_json(destination / "mcp_registry_live_summary_v0_1.json", summary)
        return summary

    downstream = _run_downstream(destination, max_servers=max_servers, mode=mode)
    export = downstream["export"]
    public_beta_candidates = {
        "mode": mode,
        "live_network_used": live_network_used,
        "public_beta_ready_count": export["public_beta_ready_count"],
        "objects": json.loads((destination / "mcp_registry_public_beta_index_v0_1.json").read_text(encoding="utf-8")).get("objects", []),
    }
    _write_json(destination / "mcp_registry_live_public_beta_candidates_v0_1.json", public_beta_candidates)
    receipt = build_registry_run_receipt(
        mode=mode,
        allow_network=allow_network,
        base_url=base_url,
        endpoint=endpoint,
        max_servers=max_servers,
        raw_payload_path=str(raw_path),
        object_count=export["object_count"],
        trace_count=export["trace_count"],
        public_beta_ready_count=export["public_beta_ready_count"],
        live_network_used=live_network_used,
        errors=[*errors, *downstream["payload_validation"].get("errors", []), *downstream["object_validation"].get("errors", [])],
        warnings=[*warnings, *export.get("warnings", [])],
        next_action="Review public_beta_mcp candidates and source traces." if export["public_beta_ready_count"] else FALLBACK_MESSAGE,
    )
    receipt_path = write_registry_run_receipt(receipt, destination / "mcp_registry_live_run_receipt_v0_1.json")
    summary = summarize_live_registry_run(
        mode,
        downstream["payload_validation"],
        downstream["object_validation"],
        receipt,
    )
    summary.update(
        {
            "success": not receipt["errors"],
            "fixture_mode": export.get("fixture_mode", False),
            "receipt_path": str(receipt_path),
            "report_path": downstream["report_path"],
        }
    )
    _write_json(destination / "mcp_registry_live_summary_v0_1.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run controlled Official MCP Registry intake.")
    parser.add_argument("--allow-network", action="store_true")
    parser.add_argument("--max-servers", type=int, default=50)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--use-manual-raw-if-present", action="store_true", default=True)
    parser.add_argument("--skip-if-no-network", action="store_true")
    args = parser.parse_args()
    result = run_live_registry_intake(
        allow_network=args.allow_network,
        max_servers=args.max_servers,
        base_url=args.base_url,
        output_dir=args.output_dir,
        use_manual_raw_if_present=args.use_manual_raw_if_present,
        skip_if_no_network=args.skip_if_no_network,
    )
    print(
        "live_registry_run: "
        f"mode={result['mode']} "
        f"success={result['success']} "
        f"objects={result['object_count']} "
        f"traces={result['trace_count']} "
        f"public_beta_ready={result['public_beta_ready_count']} "
        f"live_network_used={result['live_network_used']}"
    )
    if result.get("warnings"):
        print("warnings: " + " | ".join(str(item) for item in result["warnings"]))
    if result.get("errors"):
        print("errors: " + " | ".join(str(item) for item in result["errors"]))


if __name__ == "__main__":
    main()

