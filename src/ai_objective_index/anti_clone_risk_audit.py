from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .tech_protection_audit import run_tech_protection_audit


OUTPUT_PATH = Path("public_launch") / "wave12_tech_protection" / "ANTI_CLONE_RISK_AUDIT.json"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def assess_clone_risk(
    public_code_complete: bool = True,
    public_data_reproducible: bool = True,
    private_kernel_split: bool = True,
    full_private_kernel_exposed: bool = False,
    license_permissive: bool = True,
) -> dict[str, Any]:
    if full_private_kernel_exposed:
        return {"risk_level": "HIGH", "decision": "BLOCK_OVEREXPOSED_CORE_LOGIC"}
    score = 0
    score += 2 if public_code_complete else 0
    score += 2 if public_data_reproducible else 0
    score += 1 if license_permissive else 0
    score -= 2 if private_kernel_split else 0
    risk = "LOW" if score <= 1 else "MEDIUM" if score <= 4 else "HIGH"
    decision = "PASS_ACCEPTABLE_PUBLIC_BETA_RISK" if private_kernel_split and risk in {"LOW", "MEDIUM"} else "HOLD_STRENGTHEN_PRIVATE_KERNEL"
    if license_permissive and risk == "HIGH":
        decision = "HOLD_LICENSE_REVIEW"
    return {"risk_level": risk, "decision": decision}


def run_anti_clone_risk_audit(write_result: bool = True) -> dict[str, Any]:
    tech = run_tech_protection_audit(write_result=False)
    exposed = tech["decision"].startswith("BLOCK")
    assessment = assess_clone_risk(full_private_kernel_exposed=exposed)
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        **assessment,
        "factors": {
            "public_code_completeness": "high",
            "public_data_reproducibility": "medium",
            "public_schema_completeness": "high",
            "private_kernel_separation": "present" if not exposed else "compromised",
            "operational_data_moat": "future/private",
            "community_distribution_surface": "growing",
            "license_permissiveness": "MIT permits copying/forking under terms",
            "mcp_pypi_discoverability": "increasing",
        },
        "honest_assessment": "Surface cloning is possible because AOI is public/open-source and published to PyPI. The defensible moat should be data quality, source traces, receipts, local probes, issue feedback, vertical expertise, private calibration, and distribution trust from conservative claims.",
        "mcp_registry_submission_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_anti_clone_risk_audit()
    print(f"anti_clone_risk_audit: {result['decision']} risk={result['risk_level']}")


if __name__ == "__main__":
    main()
