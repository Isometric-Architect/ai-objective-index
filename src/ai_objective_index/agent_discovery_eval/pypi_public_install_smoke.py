from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from . import PACKAGE_NAME, PYPI_PUBLIC_INSTALL_SMOKE_PATH, TARGET_VERSION, repo_root, timestamp, write_json


def _run(command: list[str], timeout: int = 240, cwd: Path | None = None) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": str(exc)[:800]}
    return {
        "command": command,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-3000:],
        "stderr": completed.stderr[-3000:],
    }


def _verification_script() -> str:
    return r'''
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
'''


def run_pypi_public_install_smoke(
    runner: Callable[[list[str], int, Path | None], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    commands: list[dict[str, Any]] = []
    verification_payload: dict[str, Any] = {}
    temp_parent = repo_root() / "data" / "generated"
    temp_parent.mkdir(parents=True, exist_ok=True)
    # Leave the temporary venv directory in data/generated. On this Windows
    # workspace, eager cleanup can fail when antivirus or pip still holds a
    # handle; generated dirs are intentionally untracked.
    root = Path(tempfile.mkdtemp(prefix="aoi_public_pypi_smoke_", dir=temp_parent))
    venv_path = root / "venv"
    commands.append(runner([sys.executable, "-m", "venv", str(venv_path)], 240, None))
    python_exe = venv_path / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if commands[-1]["ok"]:
        commands.append(
            runner(
                [str(python_exe), "-m", "pip", "install", f"{PACKAGE_NAME}=={TARGET_VERSION}"],
                300,
                None,
            )
        )
    if commands and commands[-1]["ok"]:
        verify = runner([str(python_exe), "-c", _verification_script()], 120, None)
        commands.append(verify)
        if verify["ok"]:
            try:
                verification_payload = json.loads(verify.get("stdout", "{}").strip().splitlines()[-1])
            except (json.JSONDecodeError, IndexError):
                verification_payload = {}
    if commands and commands[-1]["ok"]:
        commands.append(
            runner([str(python_exe), "-m", "ai_objective_index.agent_adoption.discover_mode", "--sample"], 120, None)
        )
    if commands and commands[-1]["ok"]:
        commands.append(
            runner([str(python_exe), "-m", "ai_objective_index.agent_adoption.preflight_mode", "--sample"], 120, None)
        )

    required = [
        verification_payload.get("version") == TARGET_VERSION,
        verification_payload.get("agent_adoption_imported") is True,
        verification_payload.get("capability_card_version") == TARGET_VERSION,
        verification_payload.get("capability_card_packaged") is True,
        verification_payload.get("agent_schema_packaged") is True,
        verification_payload.get("agent_examples_packaged") is True,
        verification_payload.get("api_examples_packaged") is True,
        bool(commands) and all(item.get("ok") for item in commands),
    ]
    if all(required):
        decision = "PASS_PYPI_PUBLIC_INSTALL_SMOKE"
        warnings: list[str] = []
    else:
        decision = "HOLD_PUBLIC_PYPI_NOT_READY"
        warnings = ["PyPI install or installed package artifact verification did not fully pass."]

    result = {
        "schema": "AOI_PyPIPublicInstallSmokeResult/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "package_name": PACKAGE_NAME,
        "target_version": TARGET_VERSION,
        "verification_payload": verification_payload,
        "commands": commands,
        "token_printed": False,
        "external_llm_api_called": False,
        "errors": [],
        "warnings": warnings,
    }
    if write_result:
        write_json(PYPI_PUBLIC_INSTALL_SMOKE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_pypi_public_install_smoke()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"pypi_public_install_smoke: {result['decision']}")


if __name__ == "__main__":
    main()
