from __future__ import annotations

import argparse
import json
from typing import Any, Callable

from . import PUBLIC_DISCOVERY_SMOKE_PATH, timestamp, write_json
from .mcp_registry_public_smoke import run_mcp_registry_public_smoke
from .pypi_public_install_smoke import run_pypi_public_install_smoke


OVERCLAIM_TERMS = [
    "security certified",
    "production ready",
    "quality guaranteed",
    "legal compliance",
    "privacy compliant",
    "license cleared",
    "action authorized",
]


def _has_overclaim(payload: dict[str, Any]) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return any(term in text for term in OVERCLAIM_TERMS)


def run_public_discovery_smoke(
    pypi_smoke: Callable[..., dict[str, Any]] = run_pypi_public_install_smoke,
    registry_smoke: Callable[..., dict[str, Any]] = run_mcp_registry_public_smoke,
    write_result: bool = True,
) -> dict[str, Any]:
    pypi = pypi_smoke(write_result=True)
    registry = registry_smoke(write_result=True)
    errors: list[str] = []
    warnings: list[str] = []

    if _has_overclaim(pypi) or _has_overclaim(registry):
        decision = "BLOCK_OVERCLAIM"
        errors.append("Public smoke artifact contains blocked overclaim wording.")
    elif pypi.get("decision") != "PASS_PYPI_PUBLIC_INSTALL_SMOKE":
        decision = "HOLD_PUBLIC_PYPI_NOT_READY"
        warnings.append(f"PyPI public install smoke is {pypi.get('decision')}.")
    elif registry.get("decision") == "PASS_MCP_REGISTRY_PUBLIC_SMOKE":
        decision = "PASS_PUBLIC_DISCOVERY_SMOKE"
    elif registry.get("decision") == "HOLD_REGISTRY_PROPAGATION":
        decision = "HOLD_REGISTRY_PROPAGATION"
        warnings.append("PyPI install passed, but MCP Registry search is still HOLD.")
    else:
        decision = registry.get("decision", "HOLD_REGISTRY_PROPAGATION")
        warnings.append(f"MCP Registry smoke is {registry.get('decision')}.")

    result = {
        "schema": "AOI_PublicDiscoverySmokeResult/v0.1",
        "generated_at": timestamp(),
        "decision": decision,
        "pypi_public_install_decision": pypi.get("decision"),
        "mcp_registry_public_smoke_decision": registry.get("decision"),
        "pypi_package_data_ok": pypi.get("verification_payload", {}),
        "mcp_registry_matches": registry.get("matches", {}),
        "token_printed": False,
        "external_llm_api_called": False,
        "publish_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(PUBLIC_DISCOVERY_SMOKE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_public_discovery_smoke()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"public_discovery_smoke: {result['decision']}")


if __name__ == "__main__":
    main()
