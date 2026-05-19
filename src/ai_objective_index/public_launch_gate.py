from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .integrated_store import get_store_for_scope


OUTPUT_DIR = Path("public_launch")
OUTPUT_PATH = OUTPUT_DIR / "PUBLIC_LAUNCH_GATE_RESULT.json"
README_CHECKLIST_PATH = OUTPUT_DIR / "PUBLIC_LAUNCH_README_CHECKLIST.md"
GO_NO_GO_PATH = OUTPUT_DIR / "GO_NO_GO_DECISION.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


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


def _public_beta_mcp_count() -> int:
    return len(get_store_for_scope("public_beta_mcp").list_objects())


def _token(condition: bool, block: bool = False) -> str:
    if block:
        return "BLOCK"
    return "PASS" if condition else "HOLD"


def write_public_launch_assets() -> list[str]:
    assets = {
        README_CHECKLIST_PATH: f"""# Public Launch README Checklist

Before any manual public switch:

- [ ] README says AOI is read-only.
- [ ] README says `public_beta_mcp` is not verified.
- [ ] README says not security certified.
- [ ] README says not a quality guarantee.
- [ ] README says not purchasing advice.
- [ ] Private GitHub link reviewed: {GITHUB_URL}
- [ ] Private Hugging Face Space reviewed: {HF_SPACE_URL}
- [ ] Private Hugging Face Dataset reviewed: {HF_DATASET_URL}
""",
        GO_NO_GO_PATH: """# GO / NO-GO Decision

## Current Private Status

AOI is staged privately on GitHub and Hugging Face.

## Option A: Keep Private

Keep all repositories private and continue internal review.

## Option B: Invite Private Reviewers

Share private links with trusted reviewers only.

## Option C: Switch Public

Only after dry-run checks pass, claim audits pass, and the human owner explicitly confirms.

## Required Checks Before Public

- `python -m pytest`
- `python -m ai_objective_index.public_launch_gate`
- `python -m ai_objective_index.public_visibility_switch --dry-run`
- `python -m ai_objective_index.public_launch_claim_audit`
- `python -m ai_objective_index.no_secrets_audit`
- `python -m ai_objective_index.launch_claim_guard`

## Human Decision

- [ ] Keep private
- [ ] Invite private reviewers
- [ ] Switch public
- [ ] Pause
""",
    }
    written: list[str] = []
    for path, text in assets.items():
        _write(path, text)
        written.append(str(path))
    return written


def run_public_launch_gate(write_result: bool = True) -> dict[str, Any]:
    private_qa = _read_json("deployment/private_deployment_v0_2/PRIVATE_DEPLOYMENT_QA_RESULT.json")
    crosslink = _read_json("deployment/private_deployment_v0_2/HF_GITHUB_CROSSLINK_AUDIT_RESULT.json")
    no_secrets = _read_json("data/generated/no_secrets_audit_result_v0_2.json")
    launch_claim = _read_json("data/generated/launch_claim_guard_result_v0_2.json")
    realdata_claim = _read_json("data/generated/realdata_claim_audit_v0_2.json")
    smoke = _read_json("data/generated/smoke_all_result_v0_1.json")
    final_preflight = _read_json("data/generated/final_preflight_result_v0_2.json")
    readme = _read_text("README.md").lower()
    public_beta_count = _public_beta_mcp_count()

    readme_boundary_ok = all(
        phrase in readme
        for phrase in ["not verified", "not security certified", "quality guarantee", "read-only"]
    )
    no_secret_findings = int(no_secrets.get("finding_count", 0) or 0)
    checks = {
        "private_deployment_qa": {"token": _token(private_qa.get("overall_token") == "PASS"), "value": private_qa.get("overall_token")},
        "crosslink_audit": {"token": _token(crosslink.get("overall_token") == "PASS"), "value": crosslink.get("overall_token")},
        "no_secrets_audit": {"token": _token(no_secret_findings == 0, block=no_secret_findings > 0), "finding_count": no_secret_findings},
        "launch_claim_guard": {"token": _token(launch_claim.get("overall_token") == "PASS"), "value": launch_claim.get("overall_token")},
        "realdata_claim_audit": {"token": _token(realdata_claim.get("overall_token") == "PASS"), "value": realdata_claim.get("overall_token")},
        "smoke_all": {"token": _token(smoke.get("pass") is True), "pass": smoke.get("pass")},
        "final_preflight": {"token": _token(final_preflight.get("overall_token") == "PASS"), "value": final_preflight.get("overall_token")},
        "public_beta_mcp": {"token": _token(public_beta_count > 0), "count": public_beta_count},
        "readme_claim_boundary": {"token": _token(readme_boundary_ok), "contains_boundary": readme_boundary_ok},
        "no_public_actions": {
            "token": "PASS",
            "public_switch_performed": False,
            "community_post_performed": False,
            "mcp_registry_submission_performed": False,
        },
    }

    if any(check["token"] == "BLOCK" for check in checks.values()):
        overall = "BLOCK"
    elif all(check["token"] == "PASS" for check in checks.values()):
        overall = "PASS"
    else:
        overall = "HOLD"

    written_assets = write_public_launch_assets()
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "checks": checks,
        "github_url": GITHUB_URL,
        "hf_space_url": HF_SPACE_URL,
        "hf_dataset_url": HF_DATASET_URL,
        "public_switch_allowed_after_manual_confirmation": overall == "PASS",
        "required_manual_confirmation": True,
        "public_switch_performed": False,
        "community_post_performed": False,
        "mcp_registry_submission_performed": False,
        "warnings": [
            "PASS means the user may decide whether to switch public; it is not product readiness.",
            "Public launch does not assert security certification, supplier verification, quality guarantee, or purchasing advice.",
        ],
        "next_action": "Decide: keep private, invite private reviewers, or explicitly confirm a public switch."
        if overall == "PASS"
        else "Resolve HOLD/BLOCK checks before any public switch.",
        "written_assets": written_assets,
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_public_launch_gate()
    print(
        "public_launch_gate: "
        f"{result['overall_token']} "
        f"public_switch_performed={result['public_switch_performed']} "
        f"required_manual_confirmation={result['required_manual_confirmation']}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
