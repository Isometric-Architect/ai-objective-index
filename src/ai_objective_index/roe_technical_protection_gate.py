from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .real_pypi_upload_gate import _repo_root
from .roe_portfolio_strategy import build_portfolio_strategy
from .roe_source_intake_audit import run_source_intake_audit


OUTPUT_PATH = Path("public_launch") / "roe0" / "ROE_TECHNICAL_PROTECTION_GATE.json"
REQUIRED_GITIGNORE_PATTERNS = [
    "/QBCPL_RUN019_INTERNAL_SOURCE_MASTER_INTEGRATION_bundle_v0_1.zip",
    "/RdsidualOps_Engine/",
    "data/generated/qbcpl_run019_extract_for_analysis_*/",
]


def _write_json(path: Path, payload: dict[str, Any], root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_gitignore(root: Path) -> str:
    path = root / ".gitignore"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def missing_gitignore_patterns(root: Path) -> list[str]:
    text = _read_gitignore(root)
    return [pattern for pattern in REQUIRED_GITIGNORE_PATTERNS if pattern not in text]


def run_protection_gate(
    write_result: bool = True,
    root: Path | None = None,
    git_files: Iterable[str] | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    strategy = build_portfolio_strategy()
    source_audit = run_source_intake_audit(write_result=False, root=base, git_files=git_files)
    missing_ignore = missing_gitignore_patterns(base)
    if source_audit["decision"].startswith("BLOCK"):
        decision = "BLOCK_INTERNAL_SOURCE_EXPOSURE"
    elif missing_ignore:
        decision = "HOLD_GITIGNORE_HARDENING_REQUIRED"
    elif strategy["decision"] != "PASS_PORTFOLIO_SEQUENCE_LOCKED":
        decision = "HOLD_STRATEGY_NOT_LOCKED"
    else:
        decision = "PASS_READY_FOR_QIRA_MVP"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "source_intake_decision": source_audit["decision"],
        "portfolio_strategy_decision": strategy["decision"],
        "selected_next_package": strategy["selected_next_package"],
        "selected_next_package_name": strategy["selected_next_package_name"],
        "missing_gitignore_patterns": missing_ignore,
        "public_private_split": {
            "public_allowed": [
                "product sequence",
                "schemas and route labels",
                "high-level packet/probe/receipt language",
                "claim boundaries",
                "placeholder-only private kernel templates",
            ],
            "remain_private": [
                "ranking-weight values",
                "threshold policy",
                "anti-gaming rules",
                "provider trust priors",
                "private negative-control bank",
                "private probe seeds",
                "commercial routing policy",
            ],
        },
        "external_actions_performed": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result, root=base)
    return result


def main() -> None:
    result = run_protection_gate()
    print(f"roe_technical_protection_gate: {result['decision']} next={result['selected_next_package']}")


if __name__ == "__main__":
    main()
