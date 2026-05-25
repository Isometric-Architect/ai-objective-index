from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_DIR = Path("public_launch") / "roe2"
MANIFEST_PATH = OUTPUT_DIR / "ROE2_SHARED_ARTIFACT_MANIFEST.json"


VERTICAL_ARTIFACTS: list[dict[str, Any]] = [
    {
        "vertical_id": "qira",
        "product_name": "QIRA-Code ReleaseGate",
        "package": "QIRA-8",
        "primary_result": "public_launch/qira8/QIRA8_BUNDLE_RESULT.json",
        "claim_audit": "public_launch/qira8/QIRA_CLAIM_BOUNDARY_AUDIT.json",
        "artifact_paths": [
            "public_launch/qira8/QIRA8_ARTIFACT_MANIFEST.json",
            "public_launch/qira8/QIRA8_BUNDLE_RESULT.json",
            "public_launch/qira8/QIRA8_REVIEWER_REPORT.md",
            "public_launch/qira8/QIRA8_PR_COMMENT_DRAFT.md",
            "public_launch/qira8/QIRA8_NEXT_STEPS.md",
            "public_launch/qira8/QIRA_CLAIM_BOUNDARY_AUDIT.json",
        ],
        "public_role": "local PR/release review artifact bundle",
    },
    {
        "vertical_id": "agentsec",
        "product_name": "AgentSec Gate",
        "package": "AgentSec-5",
        "primary_result": "public_launch/agentsec5/AGENTSEC5_PACKAGE_RESULT.json",
        "claim_audit": "public_launch/agentsec5/AGENTSEC_CLAIM_BOUNDARY_AUDIT.json",
        "artifact_paths": [
            "public_launch/agentsec5/AGENTSEC5_PACKAGE_RESULT.json",
            "public_launch/agentsec5/AGENTSEC5_FIXTURE_CORPUS.json",
            "public_launch/agentsec5/AGENTSEC5_FIXTURE_CORPUS_REPORT.md",
            "public_launch/agentsec5/AGENTSEC5_NEGATIVE_CONTROL_RESULT.json",
            "public_launch/agentsec5/AGENTSEC5_NEGATIVE_CONTROL_REPORT.md",
            "public_launch/agentsec5/AGENTSEC5_NEXT_STEPS.md",
            "public_launch/agentsec5/AGENTSEC_CLAIM_BOUNDARY_AUDIT.json",
        ],
        "public_role": "local fake manifest fixture corpus and negative-control artifact",
    },
    {
        "vertical_id": "datacapsule",
        "product_name": "DataCapsule / AIDREG Engine",
        "package": "DataCapsule-4",
        "primary_result": "public_launch/datacapsule4/DATACAPSULE4_INTAKE_RESULT.json",
        "claim_audit": "public_launch/datacapsule4/DATACAPSULE4_CLAIM_BOUNDARY_AUDIT.json",
        "artifact_paths": [
            "public_launch/datacapsule4/DATACAPSULE4_INTAKE_RESULT.json",
            "public_launch/datacapsule4/DATACAPSULE4_BRIDGE_RESULT.json",
            "public_launch/datacapsule4/DATACAPSULE4_CORPUS_RESULT.json",
            "public_launch/datacapsule4/DATACAPSULE4_EVAL_LEAK_SEPARATION_REPORT.json",
            "public_launch/datacapsule4/DATACAPSULE4_NEXT_STEPS.md",
            "public_launch/datacapsule4/DATACAPSULE4_CLAIM_BOUNDARY_AUDIT.json",
        ],
        "public_role": "local data-use and corpus manifest boundary artifact",
    },
]


def _write_json(path: Path, payload: dict[str, Any], root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decision_bucket(decision: str) -> str:
    upper = decision.upper()
    if upper.startswith(("PASS", "ALLOW")):
        return "allow"
    if upper.startswith("HOLD"):
        return "hold"
    if upper.startswith("BLOCK"):
        return "block"
    return "unknown"


def _decision_counts(result: dict[str, Any]) -> dict[str, int]:
    allow = int(result.get("allow_count", 0) or 0)
    hold = int(result.get("hold_count", 0) or 0)
    block = int(result.get("block_count", 0) or 0)
    if allow or hold or block:
        return {"allow": allow, "hold": hold, "block": block}
    bucket = _decision_bucket(str(result.get("decision", "")))
    return {
        "allow": 1 if bucket == "allow" else 0,
        "hold": 1 if bucket == "hold" else 0,
        "block": 1 if bucket == "block" else 0,
    }


def _safe_flags(result: dict[str, Any]) -> dict[str, bool]:
    return {
        "local_only": bool(result.get("local_only", True)),
        "network_used": bool(result.get("network_used", False)),
        "external_actions_performed": bool(result.get("external_actions_performed", False)),
        "token_printed": bool(result.get("token_printed", False)),
        "can_authorize_action": bool(result.get("can_authorize_action", False)),
        "can_certify_security": bool(result.get("can_certify_security", False)),
        "can_certify_quality": bool(result.get("can_certify_quality", False)),
    }


def build_shared_artifact_manifest(
    root: Path | None = None,
    verticals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    selected = verticals or VERTICAL_ARTIFACTS
    vertical_entries: list[dict[str, Any]] = []
    missing_artifacts: list[str] = []
    totals = {"allow": 0, "hold": 0, "block": 0}
    for vertical in selected:
        primary_path = base / vertical["primary_result"]
        primary_result = _read_json(primary_path)
        decision = str(primary_result.get("decision", "UNKNOWN_DECISION"))
        counts = _decision_counts(primary_result)
        for key in totals:
            totals[key] += counts[key]
        artifact_entries = []
        for relative in vertical["artifact_paths"]:
            path = base / relative
            exists = path.exists()
            if not exists:
                missing_artifacts.append(relative)
            artifact_entries.append(
                {
                    "path": relative,
                    "exists": exists,
                    "bytes": path.stat().st_size if exists and path.is_file() else 0,
                    "sha256": _sha256(path),
                }
            )
        vertical_entries.append(
            {
                "vertical_id": vertical["vertical_id"],
                "product_name": vertical["product_name"],
                "package": vertical["package"],
                "public_role": vertical["public_role"],
                "primary_result": vertical["primary_result"],
                "primary_decision": decision,
                "decision_bucket": _decision_bucket(decision),
                "decision_counts": counts,
                "claim_audit": vertical["claim_audit"],
                "safe_flags": _safe_flags(primary_result),
                "known_limits": primary_result.get("known_limits", []),
                "must_not_claim": primary_result.get("must_not_claim", []),
                "artifacts": artifact_entries,
            }
        )
    decision = "PASS_ROE2_SHARED_MANIFEST_READY" if not missing_artifacts else "HOLD_ROE2_MISSING_ARTIFACTS"
    return {
        "schema": "ResidualOps_SharedArtifactManifest/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "vertical_count": len(vertical_entries),
        "totals": totals,
        "verticals": vertical_entries,
        "missing_artifacts": sorted(set(missing_artifacts)),
        "public_boundary": [
            "local artifact manifest only",
            "read-only dashboard input",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not action authorization",
        ],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }


def run_shared_artifact_manifest(write_result: bool = True, root: Path | None = None) -> dict[str, Any]:
    result = build_shared_artifact_manifest(root=root)
    if write_result:
        _write_json(MANIFEST_PATH, result, root=root)
    return result


def main() -> None:
    result = run_shared_artifact_manifest()
    print(f"residualops_artifact_manifest: {result['decision']} verticals={result['vertical_count']}")


if __name__ == "__main__":
    main()
