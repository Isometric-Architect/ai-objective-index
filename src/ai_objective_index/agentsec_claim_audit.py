from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "agentsec1" / "AGENTSEC_CLAIM_BOUNDARY_AUDIT.json"
AGENTSEC2_OUTPUT_PATH = Path("public_launch") / "agentsec2" / "AGENTSEC_CLAIM_BOUNDARY_AUDIT.json"
SCAN_PATHS = [
    Path("docs") / "agentsec_gate_plan.md",
    Path("docs") / "agentsec1_tool_risk_packet.md",
    Path("docs") / "agentsec_manifest_scanner.md",
    Path("docs") / "agentsec_limitations.md",
    Path("docs") / "agentsec2_policy_gate.md",
    Path("docs") / "agentsec_policy_profiles.md",
    Path("public_launch") / "agentsec1",
    Path("public_launch") / "agentsec2",
]

RISKY_PATTERNS = [
    re.compile(r"\bverified\s+tool\b", re.I),
    re.compile(r"\bsafe\s+tool\b", re.I),
    re.compile(r"\bsecurity\s+certified\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\bproduction[- ]ready\b", re.I),
    re.compile(r"\baction\s+authorized\b", re.I),
    re.compile(r"\blive\s+security\s+gateway\b", re.I),
    re.compile(r"\bautomatic\s+security\s+gateway\b", re.I),
]

SAFE_CONTEXT = [
    "not ",
    "no ",
    "must not",
    "do not",
    "does not",
    "without claiming",
    "claim boundary",
    "must_not_claim",
]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _iter_files() -> list[Path]:
    root = _repo_root()
    files: list[Path] = []
    for relative in SCAN_PATHS:
        path = root / relative
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ".txt"}:
            files.append(path)
        elif path.is_dir():
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file() and child.suffix.lower() in {".md", ".json", ".txt"}
            )
    return sorted(set(files))


def _safe_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in SAFE_CONTEXT)


def run_agentsec_claim_audit(write_result: bool = True) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for path in _iter_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(_repo_root())).replace("\\", "/")
        for index, line in enumerate(text.splitlines(), start=1):
            if _safe_line(line):
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": rel, "line": index, "pattern": pattern.pattern})
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": "BLOCK_AGENTSEC_OVERCLAIM" if findings else "PASS_AGENTSEC_CLAIM_BOUNDARY",
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "allowed_language": [
            "local metadata scan",
            "ToolRiskPacket",
            "permission scope",
            "source-trace or manifest evidence",
            "ALLOW/HOLD/BLOCK",
            "not verified",
            "not security certified",
        ],
        "must_not_claim": [
            "do not claim verified tool status",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim action authorization",
        ],
        "external_actions_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write_json(AGENTSEC2_OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_agentsec_claim_audit()
    print(f"agentsec_claim_audit: {result['decision']} risky_phrase_count={result['risky_phrase_count']}")


if __name__ == "__main__":
    main()
