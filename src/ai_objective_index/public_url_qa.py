from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL
from .public_beta_message_guard import audit_message_text
from .public_launch_gate import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "PUBLIC_URL_QA_RESULT.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_text(path: str | Path) -> str:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


def check_url_reachable(url: str, timeout: int = 12) -> dict[str, Any]:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "ai-objective-index-public-url-qa/0.1"})
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - explicit public URL QA.
            status = getattr(response, "status", None) or response.getcode()
            return {"checked": True, "reachable": 200 <= int(status) < 400, "status": status, "error": None}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return {"checked": False, "reachable": False, "status": None, "error": str(exc)[:300]}


def _links_recorded() -> dict[str, bool]:
    blob = "\n".join(
        [
            _read_text("README.md"),
            _read_text("docs/huggingface_demo.md"),
            _read_text("docs/community_launch.md"),
            _read_text("docs/public_beta_release_plan.md"),
            _read_text("public_launch/PUBLIC_BETA_POST_DRAFT_NO_CONTACT.md"),
        ]
    )
    return {
        "github": GITHUB_URL in blob,
        "hf_space": HF_SPACE_URL in blob,
        "hf_dataset": HF_DATASET_URL in blob,
    }


def _claim_findings(files: list[str | Path] | None = None) -> list[dict[str, Any]]:
    targets = files or [
        "README.md",
        "docs/community_launch.md",
        "docs/huggingface_demo.md",
        "public_launch/PUBLIC_BETA_POST_DRAFT_NO_CONTACT.md",
        "public_launch/COMMUNITY_POST_HOLD_NOTE.md",
    ]
    findings: list[dict[str, Any]] = []
    for item in targets:
        path = Path(item)
        if not path.is_absolute():
            path = _repo_root() / path
        if path.exists():
            result = audit_message_text(path.read_text(encoding="utf-8", errors="ignore"), str(path))
            findings.extend(result["findings"])
    return findings


def run_public_url_qa(
    url_checker: Callable[[str], dict[str, Any]] = check_url_reachable,
    claim_files: list[str | Path] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    url_results = {
        "github": url_checker(GITHUB_URL),
        "hf_space": url_checker(HF_SPACE_URL),
        "hf_dataset": url_checker(HF_DATASET_URL),
    }
    links = _links_recorded()
    findings = _claim_findings(claim_files)
    any_checked = any(item.get("checked") for item in url_results.values())
    all_reachable_if_checked = all((not item.get("checked")) or item.get("reachable") for item in url_results.values())
    links_ok = all(links.values())

    if findings:
        overall = "BLOCK"
    elif links_ok and any_checked and all_reachable_if_checked:
        overall = "PASS"
    elif not any_checked:
        overall = "NOT_CHECKED"
    else:
        overall = "HOLD"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "github_public_checked": url_results["github"],
        "hf_space_public_checked": url_results["hf_space"],
        "hf_dataset_public_checked": url_results["hf_dataset"],
        "links": {
            "github_url": GITHUB_URL,
            "hf_space_url": HF_SPACE_URL,
            "hf_dataset_url": HF_DATASET_URL,
            "recorded": links,
        },
        "forbidden_claim_findings": findings,
        "community_post_performed": False,
        "github_release_created": False,
        "mcp_registry_submission_performed": False,
        "warnings": [
            "If URL checks are NOT_CHECKED, manually open the public URLs in a private browser.",
            "URL reachability is not a product-readiness, safety, security, or quality guarantee.",
        ],
        "next_action": "Open public URLs manually and run post_public_state_report."
        if overall in {"PASS", "NOT_CHECKED", "HOLD"}
        else "Resolve forbidden claim findings before any community announcement.",
        "read_only": True,
        "live_network_used": any_checked,
        "actual_publish_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_public_url_qa()
    print(
        "public_url_qa: "
        f"{result['overall_token']} "
        f"github_checked={result['github_public_checked']['checked']} "
        f"hf_space_checked={result['hf_space_public_checked']['checked']} "
        f"hf_dataset_checked={result['hf_dataset_public_checked']['checked']}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
