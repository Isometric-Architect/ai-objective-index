from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope
from .public_launch_gate import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "POST_PUBLIC_STABILIZATION_RESULT.json"

CLAIM_BOUNDARY_FILES = [
    "README.md",
    "docs/huggingface_demo.md",
    "docs/community_launch.md",
    "docs/public_beta_release_plan.md",
    "release/public_beta_v0_2/README_PUBLIC_BETA_v0_2.md",
    "hf_upload/space/README.md",
    "hf_upload/dataset/README.md",
    "hf_dataset/README.md",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: str | Path) -> dict[str, Any]:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_text(path: str | Path) -> str:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


def _token(condition: bool, block: bool = False) -> str:
    if block:
        return "BLOCK"
    return "PASS" if condition else "HOLD"


def _claim_boundary_summary(files: list[str | Path] | None = None) -> dict[str, Any]:
    scanned_files: list[str] = []
    blob_parts: list[str] = []
    for item in files or CLAIM_BOUNDARY_FILES:
        path = Path(item)
        if not path.is_absolute():
            path = _repo_root() / path
        if not path.exists():
            continue
        scanned_files.append(str(path.relative_to(_repo_root())) if _repo_root() in path.parents else str(path))
        blob_parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    blob = "\n".join(blob_parts).lower()
    checks = {
        "not_verified": "not verified" in blob,
        "not_security_certified": "not security certified" in blob or "not a security certification" in blob,
        "not_quality_guarantee": "not quality guarantee" in blob or "not a quality guarantee" in blob,
        "read_only": "read-only" in blob or "read only" in blob,
    }
    return {
        "token": _token(all(checks.values())),
        "checks": checks,
        "scanned_files": scanned_files,
    }


def _link_presence_summary() -> dict[str, Any]:
    blob = "\n".join(
        [
            _read_text("README.md"),
            _read_text("docs/huggingface_demo.md"),
            _read_text("docs/public_beta_release_plan.md"),
            _read_text("docs/community_launch.md"),
            _read_text("public_launch/POST_PUBLIC_REVIEW_CHECKLIST.md"),
            _read_text("public_launch/POST_PUBLIC_STATE_REPORT.json"),
        ]
    )
    links = {
        "github_url_in_docs": GITHUB_URL in blob,
        "hf_space_url_in_docs": HF_SPACE_URL in blob,
        "hf_dataset_url_in_docs": HF_DATASET_URL in blob,
    }
    return {"token": _token(all(links.values())), "links": links}


def run_post_public_stabilization(write_result: bool = True) -> dict[str, Any]:
    public_url_qa = _read_json("public_launch/PUBLIC_URL_QA_RESULT.json")
    post_public_state = _read_json("public_launch/POST_PUBLIC_STATE_REPORT.json")
    no_secrets = _read_json("data/generated/no_secrets_audit_result_v0_2.json")
    launch_claim = _read_json("data/generated/launch_claim_guard_result_v0_2.json")
    public_claim = _read_json("public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json")
    public_beta_count = len(get_store_for_scope("public_beta_mcp").list_objects())

    release_created = bool(post_public_state.get("github_release_created", False))
    community_posted = bool(post_public_state.get("community_post_performed", False))
    registry_submitted = bool(post_public_state.get("mcp_registry_submission_performed", False))
    no_secret_findings = int(no_secrets.get("finding_count", 0) or 0)
    public_claim_available = bool(public_claim)

    checks: dict[str, Any] = {
        "deployment_links_recorded": _link_presence_summary(),
        "public_url_qa": {
            "token": _token(public_url_qa.get("overall_token") == "PASS"),
            "value": public_url_qa.get("overall_token", "missing"),
        },
        "post_public_state_report": {
            "token": _token(bool(post_public_state)),
            "exists": bool(post_public_state),
        },
        "public_beta_mcp_count": {
            "token": _token(public_beta_count > 0),
            "count": public_beta_count,
        },
        "no_secrets_audit": {
            "token": _token(no_secret_findings == 0, block=no_secret_findings > 0),
            "finding_count": no_secret_findings,
            "overall_token": no_secrets.get("overall_token", "missing"),
        },
        "launch_claim_guard": {
            "token": _token(launch_claim.get("overall_token") == "PASS"),
            "value": launch_claim.get("overall_token", "missing"),
        },
        "public_launch_claim_audit": {
            "token": _token((not public_claim_available) or public_claim.get("overall_token") == "PASS"),
            "value": public_claim.get("overall_token", "not_available"),
            "available": public_claim_available,
        },
        "no_community_post": {"token": _token(not community_posted, block=community_posted), "performed": community_posted},
        "no_github_release": {"token": _token(not release_created, block=release_created), "created": release_created},
        "no_mcp_registry_submission": {
            "token": _token(not registry_submitted, block=registry_submitted),
            "performed": registry_submitted,
        },
        "claim_boundaries": _claim_boundary_summary(),
    }

    if any(check["token"] == "BLOCK" for check in checks.values()):
        overall = "BLOCK"
    elif all(check["token"] == "PASS" for check in checks.values()):
        overall = "PASS"
    else:
        overall = "HOLD"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "checks": checks,
        "github_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "public_beta_mcp_count": public_beta_count,
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "warnings": [
            "Post-public stabilization is not a community launch.",
            "Public visibility is not verification, security certification, quality guarantee, or purchasing advice.",
        ],
        "next_action": "Activate the GitHub issue loop and observe for 72 hours."
        if overall == "PASS"
        else "Resolve HOLD/BLOCK checks before any community launch or GitHub Release.",
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_post_public_stabilization()
    print(
        "post_public_stabilization: "
        f"{result['overall_token']} "
        f"public_beta_mcp={result['public_beta_mcp_count']} "
        f"community_post_performed={result['community_post_performed']}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
