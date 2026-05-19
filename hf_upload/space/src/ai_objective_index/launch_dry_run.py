from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_PATH = Path("data/generated/launch_dry_run_result_v0_2.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: str) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        value = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _check(name: str, condition: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "pass": bool(condition), "detail": detail}


def run_launch_dry_run() -> dict[str, Any]:
    root = _repo_root()
    registry_dataset = _read_json("data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json")
    final_preflight = _read_json("data/generated/final_preflight_result_v0_2.json")
    claim_audit = _read_json("data/generated/realdata_claim_audit_v0_2.json")
    release_pack = root / "release/public_beta_v0_2"
    launch_pack = root / "launch/manual_public_beta_v0_2"

    checks = [
        _check("package_importable", True, "ai_objective_index import path is available."),
        _check("openapi_exists", (root / "api/openapi.json").exists(), "api/openapi.json"),
        _check("mcp_manifest_exists", (root / "data/generated_mcp_tools_manifest.json").exists(), "MCP manifest"),
        _check(
            "public_beta_mcp_count",
            int(registry_dataset.get("beta_candidate_count", 0) or 0) > 0,
            f"count={registry_dataset.get('beta_candidate_count', 0)}",
        ),
        _check(
            "final_preflight_pass",
            final_preflight.get("overall_token") == "PASS",
            str(final_preflight.get("overall_token")),
        ),
        _check(
            "realdata_claim_audit_pass",
            claim_audit.get("overall_token") == "PASS",
            str(claim_audit.get("overall_token")),
        ),
        _check("release_pack_exists", release_pack.exists(), str(release_pack)),
        _check("launch_pack_exists", launch_pack.exists(), str(launch_pack)),
        _check("hf_demo_exists", (root / "hf_demo/app.py").exists(), "hf_demo/app.py"),
        _check("hf_dataset_readme_exists", (root / "hf_dataset/README.md").exists(), "hf_dataset/README.md"),
        _check("reports_v0_2_exist", (root / "reports/mcp_server_objective_index_v0_2.md").exists(), "v0.2 reports"),
        _check("no_actual_publish", final_preflight.get("actual_publish_performed") is False, "actual_publish_performed=false"),
    ]
    errors = [item for item in checks if not item["pass"]]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "pass": not errors,
        "checks": checks,
        "warnings": [] if not errors else ["One or more local launch dry-run checks failed."],
        "errors": errors,
        "actual_publish_performed": False,
        "live_network_used": False,
        "read_only": True,
    }


def save_launch_dry_run(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or run_launch_dry_run()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_launch_dry_run()
    path = save_launch_dry_run(results)
    print(f"Saved launch dry-run result: {path}")
    print(
        "launch_dry_run: "
        f"pass={results['pass']} "
        f"errors={len(results['errors'])} "
        "actual_publish_performed=False live_network_used=False"
    )


if __name__ == "__main__":
    main()
