from __future__ import annotations

from pathlib import Path

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_discovery_personas import OUTREACH_DIR


FEEDBACK_FORM_PATH = OUTREACH_DIR / "PILOT_FEEDBACK_INTAKE_FORM_TEMPLATE.md"


def build_feedback_intake_form() -> str:
    return """# Pilot Feedback Intake Form Template

This template is for local/offline feedback only. It does not send, upload, post, or create a live form service.

## Review Context

- Which artifact did you review?
- Which vertical did you review? AgentSec / QIRA / DataCapsule / Portfolio
- Are you the owner, maintainer, data steward, internal reviewer, external reviewer, or other?

## Feedback

- What was confusing?
- Which claim seemed too strong?
- Which ALLOW/HOLD/BLOCK finding seemed wrong?
- What evidence would you want before a second-run receipt?
- What missing fixture or negative-control case should be added?

## Local Pilot Consent

- Would you consent to a local/offline pilot using a redacted artifact that you provide?
- Which artifacts are allowed for local review?
- Which artifacts are not allowed?

## Do Not Include

Do not include tokens, passwords, private keys, raw PII, private datasets, private kernel details, credentials, or live connector secrets.

This is not certification, product readiness review, legal advice, privacy review, license clearance, eval-clean proof, or external action authorization.
"""


def write_feedback_intake_form(path: Path = FEEDBACK_FORM_PATH) -> str:
    content = build_feedback_intake_form()
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return content
