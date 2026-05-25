from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .policy_gate import build_policy_gate_markdown, build_policy_gate_result, developer_default_profile


OUTPUT_DIR = Path("public_launch") / "agentsec6"
SAMPLE_CORPUS_PATH = OUTPUT_DIR / "AGENTSEC6_SAMPLE_MANIFEST_CORPUS.json"
INTAKE_RESULT_PATH = OUTPUT_DIR / "AGENTSEC6_CORPUS_INTAKE_RESULT.json"
POLICY_GATE_RESULT_PATH = OUTPUT_DIR / "AGENTSEC6_POLICY_GATE_RESULT.json"
CORPUS_REPORT_PATH = OUTPUT_DIR / "AGENTSEC6_CORPUS_REPORT.md"


SAMPLE_MANIFEST_CORPUS: list[dict[str, Any]] = [
    {
        "name": "fixture-local-metadata-reader",
        "id": "fixture.local/local-metadata-reader",
        "provider": "local-fixture",
        "integration_type": "mcp_server",
        "description": "Reads and summarizes MCP manifest metadata already supplied by the caller.",
        "permissions": {
            "network_access": False,
            "file_access": False,
            "write_access": False,
            "secret_access": False,
            "browser_access": False,
            "code_execution": False,
        },
    },
    {
        "name": "fixture-browser-research-helper",
        "id": "fixture.local/browser-research-helper",
        "provider": "local-fixture",
        "integration_type": "mcp_server",
        "description": "Uses browser and network capabilities for operator-reviewed research tasks.",
        "permissions": {
            "network_access": True,
            "file_access": False,
            "write_access": False,
            "secret_access": False,
            "browser_access": True,
            "code_execution": False,
        },
    },
    {
        "name": "fixture-repo-file-review-helper",
        "id": "fixture.local/repo-file-review-helper",
        "provider": "local-fixture",
        "integration_type": "tool_manifest",
        "description": "Reads repository files supplied by the caller for local metadata review.",
        "permissions": {
            "network_access": False,
            "file_access": True,
            "write_access": False,
            "secret_access": False,
            "browser_access": False,
            "code_execution": False,
        },
    },
    {
        "name": "fixture-checkout-helper",
        "id": "fixture.local/checkout-helper",
        "provider": "local-fixture",
        "integration_type": "agent_tool",
        "description": "Completes login, payment, purchase, booking, and contract workflows.",
        "permissions": {
            "network_access": True,
            "file_access": False,
            "write_access": True,
            "secret_access": False,
            "browser_access": False,
            "code_execution": False,
        },
    },
    {
        "name": "fixture-security-claim-helper",
        "id": "fixture.local/security-claim-helper",
        "provider": "local-fixture",
        "integration_type": "api",
        "description": "Fixture with unsupported positive product-claim flags encoded in metadata.",
        "claims": {
            "security_certified": True,
            "safe_tool": True,
            "production_ready": True,
        },
        "permissions": {
            "network_access": False,
            "file_access": False,
            "write_access": False,
            "secret_access": False,
            "browser_access": False,
            "code_execution": False,
        },
    },
]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest_corpus(path: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    resolved = path if path.is_absolute() else _repo_root() / path
    payloads: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    if not resolved.exists():
        return [], warnings, [f"manifest corpus path not found: {path}"]
    if resolved.is_dir():
        for child in sorted(resolved.iterdir()):
            if child.is_dir():
                continue
            if child.suffix.lower() != ".json":
                warnings.append(f"unsupported manifest file ignored: {child.name}")
                continue
            try:
                payload = _read_json(child)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{child.name}: {exc}")
                continue
            if isinstance(payload, dict):
                payloads.append(payload)
            elif isinstance(payload, list):
                payloads.extend(item for item in payload if isinstance(item, dict))
        return payloads, warnings, errors
    try:
        payload = _read_json(resolved)
    except (OSError, json.JSONDecodeError) as exc:
        return [], warnings, [str(exc)]
    if isinstance(payload, dict) and isinstance(payload.get("manifests"), list):
        payloads = [item for item in payload["manifests"] if isinstance(item, dict)]
    elif isinstance(payload, list):
        payloads = [item for item in payload if isinstance(item, dict)]
    elif isinstance(payload, dict):
        payloads = [payload]
    else:
        errors.append("manifest corpus must be a JSON object, JSON list, or directory of JSON objects")
    return payloads, warnings, errors


def _package_decision(error_count: int, manifest_count: int) -> str:
    if error_count:
        return "BLOCK_AGENTSEC6_INVALID_MANIFEST_CORPUS"
    if manifest_count == 0:
        return "HOLD_AGENTSEC6_EMPTY_MANIFEST_CORPUS"
    return "PASS_AGENTSEC6_LOCAL_CORPUS_INTAKE"


def build_agentsec6_corpus_intake_result(
    payloads: list[dict[str, Any]],
    corpus_path: str = "<memory>",
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
) -> dict[str, Any]:
    active_warnings = warnings or []
    active_errors = errors or []
    profile = developer_default_profile()
    gate_result = build_policy_gate_result(payloads, profile=profile, manifest_set_path=corpus_path)
    decision = _package_decision(len(active_errors), len(payloads))
    return {
        "schema": "AgentSec6_CorpusIntakeResult/v0.1",
        "generated_at": _now(),
        "decision": decision,
        "corpus_path": corpus_path,
        "manifest_count": len(payloads),
        "policy_gate_decision": gate_result.decision,
        "profile_id": gate_result.profile.profile_id,
        "allow_count": gate_result.allow_count,
        "hold_count": gate_result.hold_count,
        "block_count": gate_result.block_count,
        "packet_ids": [packet.packet_id for packet in gate_result.packets],
        "warnings": active_warnings,
        "errors": active_errors,
        "known_limits": [
            "local repository-supplied manifest corpus only",
            "no live MCP call",
            "no external tool execution",
            "no URL fetch",
            "not verification",
            "not security certification",
            "not quality guarantee",
            "not product-readiness proof",
            "not action authorization",
        ],
        "must_not_claim": [
            "do not claim verified tool status",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim live gateway protection",
            "do not claim external action authorization",
            "do not claim legal compliance",
        ],
        "local_only": True,
        "network_used": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "external_actions_performed": False,
        "token_printed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
        "policy_gate_result": gate_result.model_dump(mode="json", by_alias=True),
    }


def build_agentsec6_corpus_report(result: dict[str, Any]) -> str:
    gate = result["policy_gate_result"]
    rows = "\n".join(
        "| `{tool}` | `{decision}` | `{integration}` | `{provider}` |".format(
            tool=packet["tool_id"],
            decision=packet["risk_decision"],
            integration=packet["integration_type"],
            provider=packet["provider"],
        )
        for packet in gate["packets"]
    )
    warnings = "\n".join(f"- {item}" for item in result["warnings"]) or "- No warnings recorded."
    errors = "\n".join(f"- {item}" for item in result["errors"]) or "- No errors recorded."
    return f"""# AgentSec-6 Local Manifest Corpus Report

Decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Manifests | `{result['manifest_count']}` |
| Policy gate | `{result['policy_gate_decision']}` |
| ALLOW metadata-only | `{result['allow_count']}` |
| HOLD review | `{result['hold_count']}` |
| BLOCK policy risk | `{result['block_count']}` |
| Live MCP calls | `False` |
| External tool execution | `False` |
| URL fetch | `False` |

## Packet Decisions

| Tool | Decision | Integration | Provider |
| --- | --- | --- | --- |
{rows}

## Warnings

{warnings}

## Errors

{errors}

## Boundary

AgentSec-6 is a local manifest corpus ingestion artifact. It does not call live MCP servers, execute tools, fetch URLs, handle tokens, certify security, guarantee quality, prove product readiness, provide live gateway protection, or authorize external actions.
"""


def write_agentsec6_sample_outputs() -> dict[str, Any]:
    _write_json(SAMPLE_CORPUS_PATH, {"schema": "AgentSec6_SampleManifestCorpus/v0.1", "manifests": SAMPLE_MANIFEST_CORPUS})
    result = build_agentsec6_corpus_intake_result(
        SAMPLE_MANIFEST_CORPUS,
        corpus_path=str(SAMPLE_CORPUS_PATH).replace("\\", "/"),
    )
    _write_json(INTAKE_RESULT_PATH, result)
    _write_json(POLICY_GATE_RESULT_PATH, result["policy_gate_result"])
    _write_text(CORPUS_REPORT_PATH, build_agentsec6_corpus_report(result))
    return result


def run_agentsec6_corpus_ingest(path: Path | None = None, write_result: bool = True) -> dict[str, Any]:
    if path is None:
        result = write_agentsec6_sample_outputs()
        return result
    payloads, warnings, errors = load_manifest_corpus(path)
    result = build_agentsec6_corpus_intake_result(payloads, corpus_path=str(path).replace("\\", "/"), warnings=warnings, errors=errors)
    if write_result:
        _write_json(INTAKE_RESULT_PATH, result)
        _write_json(POLICY_GATE_RESULT_PATH, result["policy_gate_result"])
        _write_text(CORPUS_REPORT_PATH, build_agentsec6_corpus_report(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AgentSec-6 local manifest corpus ingestion.")
    parser.add_argument("--manifest-corpus", type=Path, help="Local JSON file or directory of JSON manifests.")
    parser.add_argument("--run-sample", action="store_true", help="Write public AgentSec-6 sample outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_agentsec6_corpus_ingest(args.manifest_corpus, write_result=True)
    print(
        "agentsec6_corpus_ingest: "
        f"{result['decision']} manifests={result['manifest_count']} "
        f"allow={result['allow_count']} hold={result['hold_count']} block={result['block_count']}"
    )


if __name__ == "__main__":
    main()
