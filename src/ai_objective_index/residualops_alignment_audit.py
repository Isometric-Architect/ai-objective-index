from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OUTPUT_PATH = Path("public_launch") / "wave8" / "RESIDUALOPS_ALIGNMENT_AUDIT.json"

REQUIRED_CONCEPTS = {
    "objective_or_q": ["objective", " q ", "query"],
    "front_readout_or_f": ["metadata", "front readout", " f "],
    "target_decision_or_q": ["route decision", "target decision", " q "],
    "residual_channel": ["residual", "missing fields", "evidence sidecar"],
    "receipt": ["receipt"],
    "d_raw_d_eco_or_coverage": ["d_raw", "d_eco", "coverage", "source trace coverage"],
    "allow_hold_block": ["allow", "hold", "block"],
    "no_action_authorization": ["no action authorization", "no external action authorization", "not action authorization"],
}
BLOCK_PHRASES = [
    "executable residualops engine",
    "external action license",
    "license token authorizes",
    "action authorization system",
    "security readiness certified",
    "trust guarantee",
    "probe pass means trust",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_docs(extra_text: str = "") -> str:
    root = _repo_root()
    paths = [
        root / "README.md",
        root / "docs" / "vnext" / "aoi_vnext_strategy.md",
        root / "docs" / "vnext" / "capability_trust_router.md",
        root / "docs" / "vnext" / "execution_receipt_loop.md",
        root / "docs" / "vnext" / "probe_before_use.md",
        root / "docs" / "vnext" / "do_not_overclaim_vnext.md",
        root / "docs" / "vnext" / "residualops_alignment.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in paths if path.exists())
    return text + "\n" + extra_text


def audit_residualops_alignment_text(text: str) -> dict[str, Any]:
    lowered = f" {text.lower()} "
    concept_checks = {
        concept: any(marker in lowered for marker in markers)
        for concept, markers in REQUIRED_CONCEPTS.items()
    }
    block_findings = []
    for phrase in BLOCK_PHRASES:
        index = lowered.find(phrase)
        if index < 0:
            continue
        context = lowered[max(0, index - 80) : index + len(phrase) + 80]
        if any(marker in context for marker in ["not ", "no ", "does not ", "do not ", "must not ", "without "]):
            continue
        block_findings.append(phrase)
    return {"concept_checks": concept_checks, "block_findings": block_findings}


def run_residualops_alignment_audit(write_result: bool = True) -> dict[str, Any]:
    audit = audit_residualops_alignment_text(_read_docs())
    missing = [key for key, ok in audit["concept_checks"].items() if not ok]
    if any("action" in finding or "license" in finding for finding in audit["block_findings"]):
        decision = "BLOCK_ACTION_AUTH_OVERCLAIM"
    elif any("security" in finding or "guarantee" in finding for finding in audit["block_findings"]):
        decision = "BLOCK_SECURITY_OVERCLAIM"
    elif missing:
        decision = "HOLD_ALIGNMENT_DOCS_NEEDED"
    else:
        decision = "PASS_ALIGNED"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "overall_token": "PASS" if decision == "PASS_ALIGNED" else ("BLOCK" if decision.startswith("BLOCK") else "HOLD"),
        "concept_checks": audit["concept_checks"],
        "missing_concepts": missing,
        "block_findings": audit["block_findings"],
        "claim_boundary": [
            "AOI aligns with ResidualOps-style vocabulary",
            "AOI is not the full executable ResidualOps Engine",
            "AOI provides no external action authorization",
            "Probe or receipt pass is not a trust guarantee",
        ],
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        destination = _repo_root() / OUTPUT_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    result = run_residualops_alignment_audit()
    print(
        "residualops_alignment_audit: "
        f"{result['decision']} missing={len(result['missing_concepts'])}"
    )


if __name__ == "__main__":
    main()
