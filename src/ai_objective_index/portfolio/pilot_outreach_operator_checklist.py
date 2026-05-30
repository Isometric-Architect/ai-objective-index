from __future__ import annotations

from pathlib import Path

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_discovery_personas import OUTREACH_DIR


FAQ_PATH = OUTREACH_DIR / "PILOT_OUTREACH_FAQ.md"
CLAIM_BOUNDARY_PATH = OUTREACH_DIR / "PILOT_OUTREACH_CLAIM_BOUNDARY.md"
OPERATOR_CHECKLIST_PATH = OUTREACH_DIR / "PILOT_OUTREACH_OPERATOR_CHECKLIST.md"
DO_NOT_SEND_GUARD_PATH = OUTREACH_DIR / "PILOT_OUTREACH_DO_NOT_SEND_GUARD.md"
KNOWN_LIMITS_PATH = OUTREACH_DIR / "PILOT_OUTREACH_KNOWN_LIMITS.md"


def _write(path: Path, content: str) -> str:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return content


def build_operator_checklist() -> str:
    return """# Pilot Outreach Operator Checklist

- Read the claim boundary first.
- Choose one reviewer persona.
- Copy one draft manually.
- Replace TODO links after manual review.
- Do not paste secrets, tokens, passwords, credentials, or private keys.
- Do not attach raw private data, private datasets, or private kernels.
- Do not promise certification, proof, product readiness, quality guarantees, adoption, or external action.
- Ask for feedback, not adoption.
- Record any reply as a local feedback packet.
- Do not auto-send.
"""


def build_do_not_send_guard() -> str:
    return """# Pilot Outreach Do-Not-Send Guard

This package does not send anything.

- No API calls.
- No email automation.
- No DM automation.
- No community auto-post.
- No GitHub issue creation.
- No mailing list creation.
- No upload or deployment.

Manual review is required before any message is used. Feedback can request clarification or a local pilot, but it does not authorize action or certification claims.
"""


def build_claim_boundary() -> str:
    return """# Pilot Outreach Claim Boundary

ROE-18 prepares feedback-request artifacts only.

It is not:

- security certification;
- code correctness proof;
- legal, privacy, license, or eval-clean proof;
- product readiness review;
- quality guarantee;
- external action authorization;
- automated outreach.

Allowed language: static demo, local artifact, feedback request, claim boundary, ALLOW/HOLD/BLOCK, not certification, no external action.
"""


def build_faq() -> str:
    return """# Pilot Outreach FAQ

## What is being shared?

A static, redacted ResidualOps demo/share pack and feedback request draft.

## Is this a launch?

No. ROE-18 prepares manual feedback discovery materials only.

## Does this send messages?

No. There is no email, DM, GitHub issue, community post, mailing list, external API call, upload, or deployment.

## What feedback is useful?

Unclear claims, confusing workflow, wrong ALLOW/HOLD/BLOCK interpretation, missing evidence, missing verticals, or stronger claim-boundary wording.

## What should reviewers avoid sending?

Tokens, credentials, raw PII, raw private datasets, private keys, private kernel details, or live connector secrets.
"""


def build_known_limits() -> str:
    return """# Pilot Outreach Known Limits

- Manual-only copy drafts.
- No sending, posting, uploading, or deployment.
- No live connector or external action.
- No certification, proof, product-readiness, quality-guarantee, or action-authorization claim.
- Link pack may contain TODO entries where a public endpoint is not available.
- Feedback must be triaged locally before it changes any receipt or policy artifact.
"""


def write_operator_artifacts() -> dict[str, str]:
    return {
        "faq": _write(FAQ_PATH, build_faq()),
        "claim_boundary": _write(CLAIM_BOUNDARY_PATH, build_claim_boundary()),
        "operator_checklist": _write(OPERATOR_CHECKLIST_PATH, build_operator_checklist()),
        "do_not_send_guard": _write(DO_NOT_SEND_GUARD_PATH, build_do_not_send_guard()),
        "known_limits": _write(KNOWN_LIMITS_PATH, build_known_limits()),
    }
