from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .models import DataCapsule, DataCapsuleBuildResult, DataUseBoundary, DataUsePermission, RiskFlags, UseClass, UseDecision


OUTPUT_DIR = Path("public_launch") / "datacapsule1"
SAMPLE_METADATA_PATH = OUTPUT_DIR / "DATACAPSULE1_SAMPLE_METADATA.json"
CAPSULE_PATH = OUTPUT_DIR / "DATACAPSULE1_CAPSULE.json"
REPORT_PATH = OUTPUT_DIR / "DATACAPSULE1_REPORT.md"
RESULT_PATH = OUTPUT_DIR / "DATACAPSULE1_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "DATACAPSULE1_NEXT_STEPS.md"

USE_CLASSES: tuple[UseClass, ...] = ("train", "retrieve", "evaluate", "summarize", "share", "act")

SAMPLE_DATASET_METADATA: dict[str, Any] = {
    "data_id": "fixture.local/aoi-docs-corpus",
    "name": "AOI local docs corpus fixture",
    "source": "repository-local-fixture",
    "source_records": ["docs/quickstart.md", "docs/mcp_usage.md"],
    "license": "MIT",
    "privacy_level": "public_metadata",
    "transform_chain": ["metadata_supplied_by_repository", "local_capsule_builder"],
    "allowed_use": {
        "train": False,
        "retrieve": True,
        "evaluate": True,
        "summarize": True,
        "share": False,
        "act": False,
    },
    "risk_flags": {
        "privacy": False,
        "poison": False,
        "prompt_injection": False,
        "eval_leak": False,
        "stale": False,
        "contradiction": False,
    },
    "claim_boundaries": [
        "not legal sufficiency",
        "not privacy compliance",
        "not data quality guarantee",
        "no action authorization",
    ],
}

UNSUPPORTED_CLAIM_PATTERNS = [
    re.compile(r"\blegally[_\s-]+cleared\b", re.I),
    re.compile(r"\bprivacy[_\s-]+compliant\b", re.I),
    re.compile(r"\bquality[_\s-]+guaranteed\b", re.I),
    re.compile(r"\beval[_\s-]+clean\b", re.I),
    re.compile(r"\baction[_\s-]+authorized\b", re.I),
]

SAFE_CONTEXT = ["not ", "no ", "do not", "does not", "must not", "without "]


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _metadata_hash(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _short_hash(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()[:12]


def _iter_strings(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.append((child_prefix, str(key)))
            rows.extend(_iter_strings(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_iter_strings(child, f"{prefix}[{index}]"))
    elif value is not None:
        rows.append((prefix, str(value)))
    return rows


def _safe_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in SAFE_CONTEXT)


def _unsupported_claims(payload: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    for path, text in _iter_strings(payload):
        haystack = f"{path}: {text}"
        if _safe_line(haystack):
            continue
        for pattern in UNSUPPORTED_CLAIM_PATTERNS:
            if pattern.search(haystack):
                findings.append(haystack[:240])
                break
    return sorted(set(findings))


def _risk_flags(payload: dict[str, Any]) -> RiskFlags:
    supplied = payload.get("risk_flags")
    raw = supplied if isinstance(supplied, dict) else {}
    license_value = str(payload.get("license") or "").strip().lower()
    source = str(payload.get("source") or "").strip()
    source_records = payload.get("source_records") if isinstance(payload.get("source_records"), list) else []
    indicators: list[str] = []
    if not license_value or license_value == "unknown":
        indicators.append("license missing or unknown")
    if not source and not source_records:
        indicators.append("source records missing")
    return RiskFlags(
        privacy=bool(raw.get("privacy", False)),
        poison=bool(raw.get("poison", False)),
        prompt_injection=bool(raw.get("prompt_injection", False)),
        eval_leak=bool(raw.get("eval_leak", False)),
        stale=bool(raw.get("stale", False)),
        contradiction=bool(raw.get("contradiction", False)),
        rights_unknown=not license_value or license_value == "unknown",
        source_unknown=not source and not source_records,
        raw_indicators=indicators,
    )


def _allowed_map(payload: dict[str, Any]) -> dict[str, bool]:
    allowed = payload.get("allowed_use")
    if isinstance(allowed, dict):
        return {key: bool(allowed.get(key, False)) for key in USE_CLASSES}
    return {key: False for key in USE_CLASSES}


def _license_restricted(license_value: str) -> bool:
    lowered = license_value.lower()
    return any(term in lowered for term in ["no commercial", "non-commercial", "restricted", "all rights reserved"])


def _use_boundary(use_class: UseClass, payload: dict[str, Any], risks: RiskFlags, unsupported_claims: list[str]) -> DataUseBoundary:
    allowed = _allowed_map(payload)
    license_value = str(payload.get("license") or "unknown")
    reasons: list[str] = []
    evidence_required: list[str] = []
    decision: UseDecision

    if unsupported_claims:
        return DataUseBoundary(
            use_class=use_class,
            decision="BLOCK_UNSUPPORTED_CLAIM",
            allowed=False,
            reasons=["unsupported legal/privacy/quality/action claim detected"],
            evidence_required=["remove or substantiate unsupported public claim"],
        )
    if use_class == "act":
        return DataUseBoundary(
            use_class=use_class,
            decision="BLOCK_ACTION_USE",
            allowed=False,
            reasons=["data capsule metadata cannot authorize external actions"],
            evidence_required=["separate action license and execution gate required"],
        )
    if risks.privacy and use_class in {"train", "share"}:
        return DataUseBoundary(
            use_class=use_class,
            decision="BLOCK_PRIVACY_RISK",
            allowed=False,
            reasons=["privacy risk flag present for broad data use"],
            evidence_required=["privacy review and minimization evidence"],
        )
    if _license_restricted(license_value) and use_class in {"train", "share"}:
        return DataUseBoundary(
            use_class=use_class,
            decision="BLOCK_LICENSE_RESTRICTED",
            allowed=False,
            reasons=["license metadata indicates restricted use"],
            evidence_required=["explicit rights evidence for requested use"],
        )
    if risks.rights_unknown and use_class in {"train", "share"}:
        return DataUseBoundary(
            use_class=use_class,
            decision="HOLD_SOURCE_RIGHTS_REVIEW",
            allowed=False,
            reasons=["license or rights metadata is missing"],
            evidence_required=["license record", "source provenance record"],
        )
    if risks.source_unknown:
        return DataUseBoundary(
            use_class=use_class,
            decision="HOLD_SOURCE_RIGHTS_REVIEW",
            allowed=False,
            reasons=["source record is missing"],
            evidence_required=["source record"],
        )
    if risks.prompt_injection and use_class in {"retrieve", "summarize"}:
        return DataUseBoundary(
            use_class=use_class,
            decision="HOLD_PROMPT_INJECTION_REVIEW",
            allowed=False,
            reasons=["prompt-injection risk flag present for retrieval or summarization use"],
            evidence_required=["local prompt-injection review and separation notes"],
        )
    if risks.eval_leak and use_class == "evaluate":
        return DataUseBoundary(
            use_class=use_class,
            decision="HOLD_EVAL_LEAK_REVIEW",
            allowed=False,
            reasons=["eval leak risk flag present"],
            evidence_required=["train/eval separation evidence"],
        )
    if risks.stale and use_class in {"retrieve", "summarize"}:
        return DataUseBoundary(
            use_class=use_class,
            decision="HOLD_STALENESS_REVIEW",
            allowed=False,
            reasons=["stale data flag present"],
            evidence_required=["freshness review"],
        )
    if not allowed.get(use_class, False):
        return DataUseBoundary(
            use_class=use_class,
            decision="HOLD_SOURCE_RIGHTS_REVIEW",
            allowed=False,
            reasons=[f"{use_class} use is not explicitly allowed by supplied metadata"],
            evidence_required=[f"explicit {use_class} permission"],
        )
    decision = "ALLOW_USE"
    reasons.append(f"{use_class} use explicitly allowed by supplied local metadata")
    return DataUseBoundary(use_class=use_class, decision=decision, allowed=True, reasons=reasons)


def _permissions(payload: dict[str, Any], risks: RiskFlags, unsupported_claims: list[str]) -> DataUsePermission:
    boundaries = {use_class: _use_boundary(use_class, payload, risks, unsupported_claims) for use_class in USE_CLASSES}
    return DataUsePermission(**boundaries)


def build_datacapsule_from_metadata(payload: dict[str, Any], metadata_path: str = "<memory>") -> DataCapsule:
    risks = _risk_flags(payload)
    unsupported = _unsupported_claims(payload)
    data_id = str(payload.get("data_id") or payload.get("id") or payload.get("name") or "unknown-data")
    name = str(payload.get("name") or data_id)
    transform_chain = payload.get("transform_chain") if isinstance(payload.get("transform_chain"), list) else []
    source_records = payload.get("source_records") if isinstance(payload.get("source_records"), list) else []
    permissions = _permissions(payload, risks, unsupported)
    residual_notes = list(risks.raw_indicators)
    if unsupported:
        residual_notes.extend(unsupported)
    if not residual_notes:
        residual_notes.append("local metadata capsule built; this is still not rights, privacy, or quality certification")
    return DataCapsule(
        capsule_id=f"datacapsule-{_short_hash(payload)}",
        data_id=data_id[:160],
        name=name[:160],
        source=str(payload.get("source") or ""),
        raw_hash=_metadata_hash(payload),
        transform_chain=[str(item)[:160] for item in transform_chain],
        license=str(payload.get("license") or "unknown"),
        privacy_level=str(payload.get("privacy_level") or "unknown"),
        source_records=[str(item)[:240] for item in source_records],
        use_permissions=permissions,
        risk_flags=risks,
        residual_notes=sorted(set(residual_notes)),
    )


def _counts(capsule: DataCapsule) -> tuple[int, int, int]:
    decisions = [getattr(capsule.use_permissions, use_class).decision for use_class in USE_CLASSES]
    allow_count = sum(1 for decision in decisions if decision == "ALLOW_USE")
    hold_count = sum(1 for decision in decisions if decision.startswith("HOLD"))
    block_count = sum(1 for decision in decisions if decision.startswith("BLOCK"))
    return allow_count, hold_count, block_count


def build_datacapsule_result(capsule: DataCapsule, metadata_path: str, capsule_path: Path = CAPSULE_PATH, report_path: Path = REPORT_PATH) -> DataCapsuleBuildResult:
    allow_count, hold_count, block_count = _counts(capsule)
    if block_count:
        decision = "BLOCK_DATACAPSULE1_USE_RISK"
    elif hold_count:
        decision = "HOLD_DATACAPSULE1_REVIEW_REQUIRED"
    else:
        decision = "PASS_DATACAPSULE1_LOCAL_CAPSULE"
    return DataCapsuleBuildResult(
        result_id=f"datacapsule-result-{capsule.capsule_id.removeprefix('datacapsule-')}",
        decision=decision,
        metadata_path=metadata_path,
        capsule_path=str(capsule_path).replace("\\", "/"),
        report_path=str(report_path).replace("\\", "/"),
        allow_count=allow_count,
        hold_count=hold_count,
        block_count=block_count,
        capsule=capsule,
        known_limits=[
            "local metadata only",
            "no crawling",
            "no live source verification",
            "not legal sufficiency",
            "not privacy compliance",
            "not data quality guarantee",
            "not action authorization",
        ],
    )


def build_datacapsule_report(result: DataCapsuleBuildResult) -> str:
    capsule = result.capsule
    rows = "\n".join(
        f"| `{use_class}` | `{getattr(capsule.use_permissions, use_class).decision}` | `{getattr(capsule.use_permissions, use_class).allowed}` |"
        for use_class in USE_CLASSES
    )
    residuals = "\n".join(f"- {item}" for item in capsule.residual_notes) or "- No residual notes recorded."
    return f"""# DataCapsule-1 Report

Decision: `{result.decision}`

| Field | Value |
| --- | --- |
| Data ID | `{capsule.data_id}` |
| Name | `{capsule.name}` |
| License | `{capsule.license}` |
| Privacy level | `{capsule.privacy_level}` |
| ALLOW | `{result.allow_count}` |
| HOLD | `{result.hold_count}` |
| BLOCK | `{result.block_count}` |
| Network used | `False` |
| Crawler used | `False` |
| External service used | `False` |

## Use Boundaries

| Use | Decision | Allowed |
| --- | --- | --- |
{rows}

## Residual Notes

{residuals}

## Boundaries

DataCapsule-1 is a local metadata receipt. It does not prove legal sufficiency, privacy compliance, data quality, license clearance, evaluation cleanliness, purchase suitability, or action authorization.
"""


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def read_metadata_path(path: Path) -> dict[str, Any]:
    resolved = path if path.is_absolute() else _repo_root() / path
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def build_datacapsule_sample_outputs() -> DataCapsuleBuildResult:
    _write_json(SAMPLE_METADATA_PATH, SAMPLE_DATASET_METADATA)
    capsule = build_datacapsule_from_metadata(SAMPLE_DATASET_METADATA, str(SAMPLE_METADATA_PATH).replace("\\", "/"))
    result = build_datacapsule_result(capsule, str(SAMPLE_METADATA_PATH).replace("\\", "/"))
    _write_json(CAPSULE_PATH, capsule.model_dump(mode="json", by_alias=True))
    _write_text(REPORT_PATH, build_datacapsule_report(result))
    _write_json(RESULT_PATH, result.model_dump(mode="json", by_alias=True))
    _write_text(
        NEXT_STEPS_PATH,
        """# DataCapsule-1 Next Steps

1. Add directory-level metadata intake for repository-supplied corpus manifests.
2. Add eval-leak and prompt-injection negative-control fixtures using local metadata only.
3. Keep live crawling, legal/privacy certification, and action authorization outside DataCapsule-1.
""",
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a DataCapsule-1 local metadata capsule.")
    parser.add_argument("--metadata", type=Path, help="Path to a local dataset/corpus metadata JSON file.")
    parser.add_argument("--run-sample", action="store_true", help="Write sample DataCapsule-1 outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.metadata:
        payload = read_metadata_path(args.metadata)
        capsule = build_datacapsule_from_metadata(payload, str(args.metadata).replace("\\", "/"))
        result = build_datacapsule_result(capsule, str(args.metadata).replace("\\", "/"))
        print(f"datacapsule_build: {result.decision} allow={result.allow_count} hold={result.hold_count} block={result.block_count}")
        return
    result = build_datacapsule_sample_outputs()
    print(f"datacapsule_sample: {result.decision} allow={result.allow_count} hold={result.hold_count} block={result.block_count}")


if __name__ == "__main__":
    main()
