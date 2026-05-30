from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "roe1" / "ROE1_PUBLIC_PRIVATE_ALIGNMENT_AUDIT.json"

SCAN_PATHS = [
    Path("README.md"),
    Path("CHANGELOG.md"),
    Path("docs") / "roe_portfolio_strategy.md",
    Path("docs") / "roe_public_private_split.md",
    Path("docs") / "roe_qbcpl_coding_governance.md",
    Path("docs") / "roe1_surface_alignment_gate.md",
    Path("docs") / "residualops_vertical_surface_matrix.md",
    Path("docs") / "residualops_common_kernel.md",
    Path("docs"),
    Path("public_launch") / "roe1",
    Path("public_launch") / "roe2",
    Path("public_launch") / "roe3",
    Path("public_launch") / "roe4",
    Path("public_launch") / "roe5",
    Path("public_launch") / "roe6",
    Path("public_launch") / "roe7",
    Path("public_launch") / "roe8",
    Path("public_launch") / "roe9",
    Path("public_launch") / "roe10",
    Path("public_launch") / "roe11",
    Path("public_launch") / "roe12",
    Path("public_launch") / "roe13",
    Path("public_launch") / "roe14",
    Path("public_launch") / "roe15",
    Path("public_launch") / "roe16",
    Path("public_launch") / "roe17",
    Path("public_launch") / "roe18",
    Path("public_launch") / "roe19",
    Path("pilot_dashboard"),
    Path("external_share_pack"),
    Path("pilot_outreach"),
    Path("feedback_replies"),
]

RISKY_PATTERNS = [
    ("overclaim", re.compile(r"\bverified\s+capability\b", re.I)),
    ("overclaim", re.compile(r"\bsafe\s+tool\b", re.I)),
    ("overclaim", re.compile(r"\bsecurity\s+certified\b", re.I)),
    ("overclaim", re.compile(r"\bquality\s+guaranteed\b", re.I)),
    ("overclaim", re.compile(r"\bproduction\s+ready\b", re.I)),
    ("overclaim", re.compile(r"\blegal\s+sufficiency\s+confirmed\b", re.I)),
    ("overclaim", re.compile(r"\bprivacy\s+compliant\b", re.I)),
    ("overclaim", re.compile(r"\beval\s+clean\b", re.I)),
    ("overclaim", re.compile(r"\baction\s+authorized\b", re.I)),
    ("overclaim", re.compile(r"\bexternal\s+action\s+authorization\b", re.I)),
    ("private_kernel", re.compile(r"\bprivate\s+ranking\s+weights?\s*[:=]\s*\d", re.I)),
    ("private_kernel", re.compile(r"\bprovider\s+trust\s+prior\s*[:=]\s*\d", re.I)),
    ("private_kernel", re.compile(r"\banti-gaming\s+threshold\s*[:=]\s*\d", re.I)),
    ("private_kernel", re.compile(r"\bprivate\s+negative-control\s+seed\s*[:=]", re.I)),
    ("private_kernel", re.compile(r"\bcommercial\s+routing\s+policy\s*[:=]\s*\d", re.I)),
]

SAFE_CONTEXT = [
    "not ",
    "is not",
    "no ",
    "do not",
    "does not",
    "cannot ",
    "without ",
    "must not",
    "remain private",
    "remains private",
    "non-public",
    "private / should not be public",
    "must_not_claim",
    "claim boundary",
]


def _write_json(path: Path, payload: dict[str, Any], root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _candidate_files(root: Path, paths: list[Path] | None = None) -> list[Path]:
    selected = paths or SCAN_PATHS
    files: list[Path] = []
    for relative in selected:
        path = root / relative
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt", ".yml", ".yaml"}:
            files.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in {".md", ".json", ".txt", ".yml", ".yaml"}:
                    name = child.name.lower()
                    if name.endswith(".schema.json"):
                        continue
                    if any(part in child.parts for part in {"dist", "hf_upload", "hf_dataset"}):
                        continue
                    files.append(child)
    return sorted(set(files))


def _safe_line(line: str, previous_lines: list[str] | None = None) -> bool:
    lowered = line.lower()
    if any(marker in lowered for marker in SAFE_CONTEXT):
        return True
    context = "\n".join(previous_lines or []).lower()
    return any(
        marker in context
        for marker in [
            "forbidden claims",
            "forbidden framing",
            "forbidden public claims",
            "must not claim",
            "must_not_claim",
            "it is not",
            "known limits",
        ]
    )


def run_public_private_alignment_audit(
    write_result: bool = True,
    root: Path | None = None,
    paths: list[Path] | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    findings: list[dict[str, Any]] = []
    for path in _candidate_files(base, paths):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(base)).replace("\\", "/")
        lines = text.splitlines()
        for line_number, line in enumerate(lines, start=1):
            if _safe_line(line, lines[max(0, line_number - 10) : line_number - 1]):
                continue
            for finding_type, pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "path": rel,
                            "line": line_number,
                            "finding_type": finding_type,
                            "pattern": pattern.pattern,
                        }
                    )
                    break

    finding_types = {finding["finding_type"] for finding in findings}
    if "private_kernel" in finding_types:
        decision = "BLOCK_PUBLIC_PRIVATE_LEAK"
    elif "overclaim" in finding_types:
        decision = "BLOCK_OVERCLAIM"
    else:
        decision = "PASS_PUBLIC_PRIVATE_ALIGNMENT"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "finding_count": len(findings),
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "public_allowed": [
            "packet, manifest, capsule, risk packet, and task packet shapes",
            "local probe/check/result/receipt artifact shapes",
            "ALLOW/HOLD/BLOCK labels",
            "high-level CertCost, residual, d_raw/d_eco vocabulary",
            "claim boundaries and limitations",
            "opt-in CI artifact bridge shape",
        ],
        "remain_private": [
            "ranking-weight values",
            "threshold policy",
            "anti-gaming rules",
            "provider trust priors",
            "private negative-control banks",
            "private probe seeds",
            "commercial routing policy",
            "enterprise data policy",
        ],
        "external_actions_performed": False,
        "network_used": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result, root=base)
    return result


def main() -> None:
    result = run_public_private_alignment_audit()
    print(f"residualops_public_private_alignment_audit: {result['decision']} findings={result['finding_count']}")


if __name__ == "__main__":
    main()
