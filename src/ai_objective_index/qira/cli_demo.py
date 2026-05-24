from __future__ import annotations

import json
from pathlib import Path

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .releasegate import sample_release_gate_report


OUTPUT_DIR = Path("public_launch") / "qira1"


def _write_json(path: Path, payload: dict) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def run_qira_cli_demo() -> dict:
    report = sample_release_gate_report()
    report_payload = report.model_dump(mode="json", by_alias=True)
    _write_json(OUTPUT_DIR / "QIRA_1_RELEASEGATE_RESULT.json", report_payload)
    _write_json(OUTPUT_DIR / "QIRA_SAMPLE_CONTRACT.json", report.receipt.contract.model_dump(mode="json", by_alias=True))
    _write_json(OUTPUT_DIR / "QIRA_SAMPLE_PATCH_RECEIPT.json", report.receipt.model_dump(mode="json", by_alias=True))
    _write_json(OUTPUT_DIR / "QIRA_SAMPLE_ACTION_LICENSE.json", report.action_license.model_dump(mode="json", by_alias=True))
    _write_text(
        OUTPUT_DIR / "QIRA_1_NEXT_STEPS.md",
        """# QIRA-1 Next Steps

1. Add task-packet import from a user-supplied repo fixture.
2. Add patch diff parsing with path and forbidden-change checks.
3. Add a GitHub Action wrapper that consumes local receipts.
4. Keep merge, deploy, security, legal, product, and public-readiness claims separately gated.

QIRA-1 remains local/offline. It does not execute arbitrary external tools, deploy code, request tokens, or certify a patch.
""",
    )
    return report_payload


def main() -> None:
    payload = run_qira_cli_demo()
    print(f"qira_cli_demo: {payload['decision_token']} deploy={payload['summary']['deploy']}")


if __name__ == "__main__":
    main()
