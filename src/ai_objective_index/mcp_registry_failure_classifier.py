from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "wave14_mcp_registry_diagnostics" / "MCP_REGISTRY_FAILURE_CLASSIFICATION.json"

REDACTION_PATTERNS = [
    (re.compile(r"github_pat_[A-Za-z0-9_]{8,}"), "github_pat_[redacted]"),
    (re.compile(r"ghp_[A-Za-z0-9_]{8,}"), "ghp_[redacted]"),
    (re.compile(r"gho_[A-Za-z0-9_]{8,}"), "gho_[redacted]"),
    (re.compile(r"ghu_[A-Za-z0-9_]{8,}"), "ghu_[redacted]"),
    (re.compile(r"ghs_[A-Za-z0-9_]{8,}"), "ghs_[redacted]"),
    (re.compile(r"ghr_[A-Za-z0-9_]{8,}"), "ghr_[redacted]"),
    (re.compile(r"pypi-[A-Za-z0-9_\-]{8,}"), "pypi-[redacted]"),
    (re.compile(r"\bhf_[A-Za-z0-9]{8,}\b"), "hf_[redacted]"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE), "Bearer [redacted]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL), "[redacted-private-key]"),
]
TOKEN_PATTERNS = [pattern for pattern, _replacement in REDACTION_PATTERNS]


def redact_sensitive(value: Any) -> str:
    text = str(value or "")
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def token_like_present(value: Any) -> bool:
    text = str(value or "")
    return any(pattern.search(text) for pattern in TOKEN_PATTERNS)


def _combined(stdout: Any = "", stderr: Any = "", extra: Any = "") -> str:
    return f"{stdout or ''}\n{stderr or ''}\n{extra or ''}".lower()


def classify_publish_failure(
    stdout: Any = "",
    stderr: Any = "",
    returncode: int | None = None,
    validate_ok: bool | None = None,
    extra: Any = "",
) -> dict[str, Any]:
    text = _combined(stdout, stderr, extra)
    matched: list[str] = []

    if returncode == 0:
        classification = "PUBLISH_SUCCESS"
        matched.append("returncode == 0")
    elif "already" in text and ("exist" in text or "published" in text):
        classification = "VERSION_ALREADY_EXISTS"
        matched.append("already/exist")
    elif "409" in text or "conflict" in text or "duplicate" in text:
        classification = "VERSION_ALREADY_EXISTS"
        matched.append("409/conflict/duplicate")
    elif validate_ok is False or "validation failed" in text or "unprocessable entity" in text or " 422" in text:
        classification = "SERVER_JSON_INVALID"
        matched.append("validation failed / 422")
    elif (
        "not logged in" in text
        or "logged in" in text
        or "log in" in text
        or "login" in text and ("required" in text or "first" in text)
        or "authentication required" in text
    ):
        classification = "AUTH_REQUIRED"
        matched.append("login required")
    elif "unauthorized" in text or "forbidden" in text or " 401" in text or " 403" in text:
        classification = "AUTH_REQUIRED"
        matched.append("401/403/unauthorized/forbidden")
    elif "namespace" in text or "repository" in text and "match" in text or "owner" in text and "github" in text:
        classification = "NAMESPACE_MISMATCH"
        matched.append("namespace/repository/owner mismatch")
    elif (
        "proxyconnect" in text
        or "connection refused" in text
        or "connectex" in text
        or "timeout" in text
        or "no such host" in text
        or "network" in text
        or "tls" in text
        or "certificate" in text
        or "dial tcp" in text
    ):
        classification = "NETWORK_ERROR"
        matched.append("network/proxy/connectivity")
    elif "500" in text or "502" in text or "503" in text or "504" in text or "internal server" in text:
        classification = "REGISTRY_API_ERROR"
        matched.append("5xx registry response")
    elif "429" in text or "rate limit" in text:
        classification = "REGISTRY_API_ERROR"
        matched.append("rate limit")
    else:
        classification = "UNKNOWN_PUBLISH_ERROR"
        matched.append("no known failure pattern")

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "classification": classification,
        "returncode": returncode,
        "validate_ok": validate_ok,
        "matched_patterns": matched,
        "token_printed": False,
        "token_like_detected_before_redaction": token_like_present(f"{stdout}\n{stderr}\n{extra}"),
    }


def write_failure_classification(payload: dict[str, Any], path: Path = OUTPUT_PATH) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    payload = classify_publish_failure()
    write_failure_classification(payload)
    print(f"mcp_registry_failure_classifier: {payload['classification']}")


if __name__ == "__main__":
    main()
