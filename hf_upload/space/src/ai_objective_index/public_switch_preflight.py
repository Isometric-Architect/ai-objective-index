from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OUTPUT_PATH = Path("github_upload/PUBLIC_SWITCH_PREFLIGHT_RESULT.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


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


def _exists(path: str | Path) -> bool:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    return full.exists()


def _token(condition: bool, block: bool = False) -> str:
    if block:
        return "BLOCK"
    return "PASS" if condition else "HOLD"


def run_public_switch_preflight(
    no_secrets_path: str | Path = "data/generated/no_secrets_audit_result_v0_2.json",
    launch_claim_guard_path: str | Path = "data/generated/launch_claim_guard_result_v0_2.json",
    realdata_claim_audit_path: str | Path = "data/generated/realdata_claim_audit_v0_2.json",
    final_preflight_path: str | Path = "data/generated/final_preflight_result_v0_2.json",
    smoke_all_path: str | Path = "data/generated/smoke_all_result_v0_1.json",
    write_result: bool = True,
) -> dict[str, Any]:
    no_secrets = _read_json(no_secrets_path)
    launch_claim = _read_json(launch_claim_guard_path)
    realdata_claim = _read_json(realdata_claim_audit_path)
    final_preflight = _read_json(final_preflight_path)
    smoke_all = _read_json(smoke_all_path)
    registry_audit = _read_json("data/registry/registry_payload_audit_v0_1.json")
    qa = _read_json("github_upload/GITHUB_POST_UPLOAD_QA_RESULT.json")

    docs_text = "\n".join(
        [
            _read_text("README.md"),
            _read_text("release/public_beta_v0_2/README_PUBLIC_BETA_v0_2.md"),
            _read_text("launch/manual_public_beta_v0_2/FINAL_CLAIM_BOUNDARY.md"),
        ]
    ).lower()
    claim_boundary_ok = all(
        phrase in docs_text
        for phrase in ["not verified", "not security certified", "not quality", "not purchasing"]
    )
    public_beta_mcp_count = int(
        registry_audit.get("public_beta_mcp_count")
        or final_preflight.get("counts", {}).get("public_beta_mcp_count", 0)
        or 0
    )

    checks = {
        "no_secrets_audit": {
            "token": _token(int(no_secrets.get("finding_count", 1) or 0) == 0, block=int(no_secrets.get("finding_count", 0) or 0) > 0),
            "finding_count": no_secrets.get("finding_count"),
            "overall_token": no_secrets.get("overall_token"),
        },
        "launch_claim_guard": {
            "token": _token(launch_claim.get("overall_token") == "PASS"),
            "overall_token": launch_claim.get("overall_token"),
        },
        "realdata_claim_audit": {
            "token": _token(realdata_claim.get("overall_token") == "PASS"),
            "overall_token": realdata_claim.get("overall_token"),
        },
        "final_preflight": {
            "token": _token(final_preflight.get("overall_token") == "PASS"),
            "overall_token": final_preflight.get("overall_token"),
        },
        "smoke_all": {
            "token": _token(smoke_all.get("pass") is True),
            "pass": smoke_all.get("pass"),
        },
        "release_pack": {
            "token": _token(_exists("release/public_beta_v0_2") and _exists("launch/manual_public_beta_v0_2")),
        },
        "public_beta_mcp": {
            "token": _token(public_beta_mcp_count > 0),
            "count": public_beta_mcp_count,
        },
        "claim_boundary_docs": {
            "token": _token(claim_boundary_ok),
            "contains_required_boundary_language": claim_boundary_ok,
        },
        "repo_private_or_unknown": {
            "token": _token(qa.get("visibility_if_known") in {"private", "not_checked", "unknown", None}),
            "visibility_if_known": qa.get("visibility_if_known", "not_checked"),
        },
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
        "required_manual_confirmation": True,
        "public_switch_performed": False,
        "recommended_next_action": "User may manually review GitHub and decide whether to switch visibility to public."
        if overall == "PASS"
        else "Resolve HOLD/BLOCK checks before considering a manual public visibility switch.",
        "actual_publish_performed": False,
        "read_only": True,
        "live_network_used": False,
        "not_asserted": [
            "product_readiness",
            "supplier_verification",
            "security_certification",
            "quality_guarantee",
            "purchasing_advice",
        ],
    }
    if write_result:
        destination = _repo_root() / OUTPUT_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    result = run_public_switch_preflight()
    print(
        "public_switch_preflight: "
        f"{result['overall_token']} "
        f"required_manual_confirmation={result['required_manual_confirmation']} "
        "public_switch_performed=False"
    )
    print(f"next_action={result['recommended_next_action']}")


if __name__ == "__main__":
    main()
