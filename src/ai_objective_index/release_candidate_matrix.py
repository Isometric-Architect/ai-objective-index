from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_PATH = Path("data/generated/release_candidate_matrix_v0_2.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _exists(path: str) -> bool:
    return (_repo_root() / path).exists()


def _row(
    surface: str,
    evidence_file: str,
    command: str,
    known_limits: str,
    required: bool = True,
) -> dict[str, Any]:
    exists = _exists(evidence_file)
    return {
        "surface": surface,
        "status": "PASS" if exists else ("HOLD" if required else "NOT_CHECKED"),
        "evidence_file": evidence_file,
        "evidence_exists": exists,
        "command_to_verify": command,
        "known_limits": known_limits,
    }


def build_release_candidate_matrix() -> dict[str, Any]:
    rows = [
        _row("Core Engine", "src/ai_objective_index/scoring.py", "python -m pytest", "Heuristic objective score, not a quality guarantee."),
        _row("MCP tools", "src/ai_objective_index/mcp_tools.py", "python -m ai_objective_index.mcp_manifest", "Read-only tools only."),
        _row("MCP compat search/fetch", "src/ai_objective_index/mcp_compat.py", "python -m ai_objective_index.mcp_smoke", "No write/action tools."),
        _row("REST API", "src/ai_objective_index/api.py", "python -m pytest tests/test_api.py", "Local read-only API."),
        _row("OpenAPI", "api/openapi.json", "python -m ai_objective_index.openapi_export", "Schema export only; no hosted service assertion."),
        _row("HF demo assets", "hf_demo/app.py", "python hf_demo/app.py", "Local/import-safe demo; no automatic publish."),
        _row("HF dataset draft", "hf_dataset/README.md", "python -m ai_objective_index.public_beta_realdata_packager", "Dataset card draft; no upload."),
        _row("Benchmark reports", "reports/mcp_server_objective_index_v0_2.md", "python -m ai_objective_index.public_beta_realdata_packager", "Registry metadata candidates, not certification.", required=False),
        _row("Registry intake", "data/registry/registry_payload_audit_v0_1.json", "python -m ai_objective_index.registry_intake.registry_payload_audit", "Manual/raw registry payload, no scraping."),
        _row("public_beta_mcp dataset", "data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json", "python -m ai_objective_index.registry_intake.registry_beta_dataset_builder", "Candidates are not verified or security certified."),
        _row("Release pack", "release/public_beta_v0_2/README_PUBLIC_BETA_v0_2.md", "python -m ai_objective_index.public_beta_realdata_packager", "Manual publish only.", required=False),
        _row("Claim audit", "data/generated/realdata_claim_audit_v0_2.json", "python -m ai_objective_index.realdata_claim_audit", "Static phrase audit, not legal review."),
        _row("Manual publish checklist", "docs/manual_publish_checklist.md", "python -m ai_objective_index.release_candidate_matrix", "Checklist only; no publish."),
    ]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    overall = "PASS" if counts.get("HOLD", 0) == 0 and counts.get("BLOCK", 0) == 0 else "HOLD"
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "surfaces": rows,
        "status_counts": counts,
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }


def save_release_candidate_matrix(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or build_release_candidate_matrix()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = build_release_candidate_matrix()
    path = save_release_candidate_matrix(results)
    print(f"Saved release candidate matrix: {path}")
    print(
        "release_candidate_matrix: "
        f"{results['overall_token']} "
        f"surfaces={len(results['surfaces'])} "
        f"status_counts={results['status_counts']}"
    )


if __name__ == "__main__":
    main()
