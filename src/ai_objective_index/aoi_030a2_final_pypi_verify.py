from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_final_common import (
    FINAL_PYPI_UPLOAD_PATH,
    FINAL_PYPI_VERIFY_PATH,
    PACKAGE_NAME,
    TARGET_VERSION,
    now,
    read_json,
    repo_root,
    write_json,
)


ACCEPTED_UPLOAD_DECISIONS = {"UPLOAD_SUCCESS_DIRECT_TWINE_VERIFIED", "HOLD_VERSION_ALREADY_EXISTS"}


def _run(command: list[str], timeout: int = 300) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": sanitize(exc)}
    return {
        "command": command,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": sanitize(completed.stdout),
        "stderr": sanitize(completed.stderr),
    }


def _python_in_venv(venv: Path) -> Path:
    candidate = venv / "Scripts" / "python.exe"
    return candidate if candidate.exists() else venv / "bin" / "python"


def _verify_script() -> str:
    return r"""
import importlib.metadata as md
import json
import ai_objective_index
import ai_objective_index.agent_adoption.capability_card as card

dist = md.distribution("ai-objective-index")
files = [str(item).replace("\\", "/") for item in (dist.files or [])]
payload = {
    "version": ai_objective_index.__version__,
    "agent_adoption_imported": True,
    "capability_card_version": card.build_capability_card().get("version"),
    "capability_card_packaged": any(item.endswith("agent_discovery/CAPABILITY_CARD.json") for item in files),
    "agent_schema_packaged": any(item.endswith("schemas/agent/aoi_capability_card.schema.json") for item in files),
    "agent_examples_packaged": any(item.endswith("examples/agent_prompts/discover_mcp_candidates.md") for item in files),
    "api_examples_packaged": any(item.endswith("api/vnext/examples/agent/discover_request.json") for item in files),
}
print(json.dumps(payload, sort_keys=True))
"""


def run_final_pypi_verify(
    upload_result: dict[str, Any] | None = None,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    upload = upload_result if upload_result is not None else read_json(FINAL_PYPI_UPLOAD_PATH)
    warnings: list[str] = []
    errors: list[str] = []
    commands: list[dict[str, Any]] = []
    verify_payload: dict[str, Any] = {}

    if upload.get("decision") not in ACCEPTED_UPLOAD_DECISIONS:
        decision = "HOLD_PYPI_UPLOAD_NOT_CONFIRMED"
        warnings.append(f"PyPI upload result is {upload.get('decision')}.")
    else:
        tmp_root = repo_root() / "data" / "generated"
        tmp_root.mkdir(parents=True, exist_ok=True)
        venv_dir = Path(tempfile.mkdtemp(prefix="aoi_030a2_final_pypi_verify_", dir=tmp_root))
        venv = venv_dir / "venv"
        create = runner([sys.executable, "-m", "venv", str(venv)], 300)
        commands.append(create)
        python = _python_in_venv(venv)
        install = runner([str(python), "-m", "pip", "install", f"{PACKAGE_NAME}=={TARGET_VERSION}"], 600)
        commands.append(install)
        verify = runner([str(python), "-c", _verify_script()], 300)
        commands.append(verify)
        smoke = runner([str(python), "-m", "ai_objective_index.mcp_smoke"], 300)
        commands.append(smoke)
        if verify.get("stdout"):
            try:
                verify_payload = json.loads(str(verify["stdout"]).strip().splitlines()[-1])
            except json.JSONDecodeError:
                verify_payload = {}

        install_text = f"{install.get('stdout', '')}\n{install.get('stderr', '')}".lower()
        version_ok = verify_payload.get("version") == TARGET_VERSION
        package_data_ok = all(
            verify_payload.get(key) is True
            for key in [
                "agent_adoption_imported",
                "capability_card_packaged",
                "agent_schema_packaged",
                "agent_examples_packaged",
                "api_examples_packaged",
            ]
        )
        if install.get("ok") and verify.get("ok") and smoke.get("ok") and version_ok and package_data_ok:
            decision = "PASS_REAL_PYPI_INSTALL_030A2"
        elif "no matching distribution" in install_text or "not found" in install_text:
            decision = "HOLD_PYPI_NOT_PROPAGATED_OR_UPLOAD_MISSING"
            warnings.append("PyPI did not return the requested 0.3.0a2 package yet.")
        else:
            decision = "BLOCK_PYPI_VERIFY_FAILED"
            errors.append("Real PyPI install or smoke verification failed.")

    result = {
        "schema": "AOI_030A2FinalPyPIVerifyResult/v0.1",
        "generated_at": now(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "package_name": PACKAGE_NAME,
        "upload_decision": upload.get("decision"),
        "verification_payload": verify_payload,
        "commands": commands,
        "token_printed": False,
        "pypirc_created": False,
        "mcp_registry_publish_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(FINAL_PYPI_VERIFY_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_final_pypi_verify()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"aoi_030a2_final_pypi_verify: {result['decision']}")


if __name__ == "__main__":
    main()

