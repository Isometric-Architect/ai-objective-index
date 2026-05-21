from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .vnext_distribution_gate import run_vnext_distribution_gate


OUTPUT_PATH = Path("public_launch") / "wave8" / "VNEXT_PYPI_RESUME_GATE.json"
INSTRUCTIONS_PATH = Path("public_launch") / "wave8" / "NEXT_8Q_A_RESUME_INSTRUCTIONS.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_instructions(result: dict[str, Any]) -> None:
    text = f"""# Next 8Q-A Resume Instructions

Next package: 8Q-A Local Build Tool Install + Dist Build + Twine Check.

Before resuming:

- Distribution gate decision: `{result['distribution_gate_decision']}`
- Version decision: choose `0.3.0` or `0.3.0a1` before upload-oriented packages.

8Q-A will:

1. Install/check `build` and `twine` locally if needed.
2. Build wheel and sdist locally.
3. Run `twine check`.
4. Run local install smoke tests.
5. Refresh PyPI/MCP Registry readiness.

8Q-A will not upload to TestPyPI or PyPI.

The user does not need a PyPI token yet. A token is needed only in a later explicit TestPyPI upload package. Do not paste tokens into chat, save tokens in the repository, or commit `.pypirc` files.
"""
    destination = _repo_root() / INSTRUCTIONS_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def run_vnext_pypi_resume_gate(write_result: bool = True) -> dict[str, Any]:
    gate = run_vnext_distribution_gate(write_result=True)
    pyproject_exists = (_repo_root() / "pyproject.toml").exists()
    decision = "PASS_READY_FOR_8Q_A" if gate["safe_to_resume_8q_a"] and pyproject_exists else "HOLD_DISTRIBUTION_GATE"
    if gate["decision"] == "HOLD_VERSION_DECISION":
        decision = "HOLD_VERSION_DECISION_BEFORE_UPLOAD"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "overall_token": "PASS" if decision == "PASS_READY_FOR_8Q_A" else "HOLD",
        "distribution_gate_decision": gate["decision"],
        "pyproject_exists": pyproject_exists,
        "build_tool_status_required_now": False,
        "dist_required_now": False,
        "pypi_token_required_now": False,
        "next_package": "8Q-A Local Build Tool Install + Dist Build + Twine Check",
        "upload_performed": False,
        "testpypi_upload_performed": False,
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write_instructions(result)
    return result


def main() -> None:
    result = run_vnext_pypi_resume_gate()
    print(
        "vnext_pypi_resume_gate: "
        f"{result['decision']} token_required_now={result['pypi_token_required_now']}"
    )


if __name__ == "__main__":
    main()
