from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .capsule_builder import USE_CLASSES, build_datacapsule_from_metadata
from .models import CorpusManifestFile, CorpusManifestSummary, DataCapsuleCorpusBuildResult, RiskFlags
from .negative_controls import negative_control_summary, run_datacapsule_negative_controls


OUTPUT_DIR = Path("public_launch") / "datacapsule2"
SAMPLE_MANIFEST_PATH = OUTPUT_DIR / "DATACAPSULE2_SAMPLE_CORPUS_MANIFEST.json"
CAPSULE_PATH = OUTPUT_DIR / "DATACAPSULE2_CORPUS_CAPSULE.json"
RESULT_PATH = OUTPUT_DIR / "DATACAPSULE2_RESULT.json"
REPORT_PATH = OUTPUT_DIR / "DATACAPSULE2_REPORT.md"
NEGATIVE_CONTROL_PATH = OUTPUT_DIR / "DATACAPSULE2_NEGATIVE_CONTROL_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "DATACAPSULE2_NEXT_STEPS.md"


SAMPLE_CORPUS_MANIFEST: dict[str, Any] = {
    "corpus_id": "fixture.local/aoi-docs-corpus-manifest",
    "name": "AOI local docs corpus manifest fixture",
    "root_path": "docs/",
    "source": "repository-local-manifest",
    "allowed_use": {
        "train": False,
        "retrieve": True,
        "evaluate": False,
        "summarize": True,
        "share": False,
        "act": False,
    },
    "files": [
        {
            "path": "docs/mcp_usage.md",
            "source": "repository-local-doc",
            "license": "MIT",
            "privacy_level": "public_metadata",
            "purpose": ["retrieve", "summarize"],
        },
        {
            "path": "docs/api_reference.md",
            "source": "repository-local-doc",
            "license": "MIT",
            "privacy_level": "public_metadata",
            "purpose": ["retrieve", "summarize"],
        },
        {
            "path": "docs/launch_notes.md",
            "source": "repository-local-doc",
            "license": "MIT",
            "privacy_level": "public_metadata",
            "purpose": ["retrieve"],
            "risk_flags": {"stale": True},
        },
    ],
    "claim_boundaries": [
        "not legal sufficiency",
        "not privacy compliance",
        "not data quality guarantee",
        "no action authorization",
    ],
}


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _as_file_rows(manifest: dict[str, Any]) -> list[CorpusManifestFile]:
    files = manifest.get("files")
    if not isinstance(files, list):
        return []
    rows: list[CorpusManifestFile] = []
    for item in files:
        if isinstance(item, dict):
            rows.append(CorpusManifestFile(**item))
    return rows


def _aggregate_flags(files: list[CorpusManifestFile], manifest: dict[str, Any]) -> RiskFlags:
    raw_manifest_flags = manifest.get("risk_flags") if isinstance(manifest.get("risk_flags"), dict) else {}
    flags = RiskFlags(
        privacy=bool(raw_manifest_flags.get("privacy", False)),
        poison=bool(raw_manifest_flags.get("poison", False)),
        prompt_injection=bool(raw_manifest_flags.get("prompt_injection", False)),
        eval_leak=bool(raw_manifest_flags.get("eval_leak", False)),
        stale=bool(raw_manifest_flags.get("stale", False)),
        contradiction=bool(raw_manifest_flags.get("contradiction", False)),
    )
    indicators: list[str] = []
    for row in files:
        row_flags = row.risk_flags
        flags.privacy = flags.privacy or row_flags.privacy
        flags.poison = flags.poison or row_flags.poison
        flags.prompt_injection = flags.prompt_injection or row_flags.prompt_injection
        flags.eval_leak = flags.eval_leak or row_flags.eval_leak
        flags.stale = flags.stale or row_flags.stale
        flags.contradiction = flags.contradiction or row_flags.contradiction
        indicators.extend(row_flags.raw_indicators)
    flags.raw_indicators = sorted(set(indicators))
    return flags


def summarize_corpus_manifest(manifest: dict[str, Any]) -> CorpusManifestSummary:
    files = _as_file_rows(manifest)
    license_values = sorted({row.license or "unknown" for row in files})
    privacy_levels = sorted({row.privacy_level or "unknown" for row in files})
    missing_fields: list[str] = []
    if not manifest.get("corpus_id"):
        missing_fields.append("corpus_id")
    if not manifest.get("name"):
        missing_fields.append("name")
    if not files:
        missing_fields.append("files")
    for row in files:
        if not row.source:
            missing_fields.append(f"{row.path}:source")
        if not row.license or row.license == "unknown":
            missing_fields.append(f"{row.path}:license")
    return CorpusManifestSummary(
        corpus_id=str(manifest.get("corpus_id") or "unknown-corpus"),
        name=str(manifest.get("name") or manifest.get("corpus_id") or "unknown corpus"),
        root_path=str(manifest.get("root_path") or ""),
        file_count=len(files),
        source_record_count=sum(1 for row in files if row.source),
        license_values=license_values,
        privacy_levels=privacy_levels,
        risk_flags=_aggregate_flags(files, manifest),
        missing_fields=sorted(set(missing_fields)),
    )


def manifest_to_capsule_metadata(manifest: dict[str, Any]) -> dict[str, Any]:
    files = _as_file_rows(manifest)
    summary = summarize_corpus_manifest(manifest)
    allowed = manifest.get("allowed_use") if isinstance(manifest.get("allowed_use"), dict) else {}
    return {
        "data_id": summary.corpus_id,
        "name": summary.name,
        "source": str(manifest.get("source") or "local-corpus-manifest"),
        "source_records": [row.path for row in files],
        "license": "mixed" if len(summary.license_values) > 1 else (summary.license_values[0] if summary.license_values else "unknown"),
        "privacy_level": "mixed" if len(summary.privacy_levels) > 1 else (summary.privacy_levels[0] if summary.privacy_levels else "unknown"),
        "transform_chain": ["repository_supplied_corpus_manifest", "datacapsule2_local_manifest_intake"],
        "allowed_use": {use_class: bool(allowed.get(use_class, False)) for use_class in USE_CLASSES},
        "risk_flags": summary.risk_flags.model_dump(mode="json"),
        "claim_boundaries": manifest.get("claim_boundaries", []),
    }


def build_corpus_manifest_result(manifest: dict[str, Any], manifest_path: str) -> DataCapsuleCorpusBuildResult:
    summary = summarize_corpus_manifest(manifest)
    capsule = build_datacapsule_from_metadata(manifest_to_capsule_metadata(manifest), manifest_path)
    controls = run_datacapsule_negative_controls()
    control_stats = negative_control_summary(controls)
    decisions = [getattr(capsule.use_permissions, use_class).decision for use_class in USE_CLASSES]
    hold_count = sum(1 for decision in decisions if decision.startswith("HOLD"))
    block_count = sum(1 for decision in decisions if decision.startswith("BLOCK"))
    if control_stats["false_pass_count"] or block_count:
        decision = "BLOCK_DATACAPSULE2_USE_RISK"
    elif hold_count or summary.missing_fields:
        decision = "HOLD_DATACAPSULE2_REVIEW_REQUIRED"
    else:
        decision = "PASS_DATACAPSULE2_LOCAL_CORPUS_MANIFEST"
    return DataCapsuleCorpusBuildResult(
        result_id=f"datacapsule2-{capsule.capsule_id.removeprefix('datacapsule-')}",
        decision=decision,
        manifest_path=manifest_path,
        capsule_path=str(CAPSULE_PATH).replace("\\", "/"),
        report_path=str(REPORT_PATH).replace("\\", "/"),
        summary=summary,
        capsule=capsule,
        negative_controls=controls,
        negative_control_false_pass_count=int(control_stats["false_pass_count"]),
        known_limits=[
            "local manifest metadata only",
            "no directory crawling",
            "no file content inspection unless supplied in manifest metadata",
            "no live source verification",
            "not legal sufficiency",
            "not privacy compliance",
            "not data quality guarantee",
            "not action authorization",
        ],
    )


def build_corpus_manifest_report(result: DataCapsuleCorpusBuildResult) -> str:
    capsule = result.capsule
    rows = "\n".join(
        f"| `{use_class}` | `{getattr(capsule.use_permissions, use_class).decision}` | `{getattr(capsule.use_permissions, use_class).allowed}` |"
        for use_class in USE_CLASSES
    )
    controls = "\n".join(
        f"| `{control.control_id}` | `{control.expected_decision}` | `{control.actual_decision}` | `{control.result}` |"
        for control in result.negative_controls
    )
    missing = "\n".join(f"- {item}" for item in result.summary.missing_fields) or "- No missing manifest fields recorded."
    return f"""# DataCapsule-2 Corpus Manifest Report

Decision: `{result.decision}`

| Field | Value |
| --- | --- |
| Corpus ID | `{result.summary.corpus_id}` |
| Name | `{result.summary.name}` |
| File count | `{result.summary.file_count}` |
| Source record count | `{result.summary.source_record_count}` |
| Negative-control false passes | `{result.negative_control_false_pass_count}` |
| Network used | `False` |
| Crawler used | `False` |
| External service used | `False` |

## Use Boundaries

| Use | Decision | Allowed |
| --- | --- | --- |
{rows}

## Negative Controls

| Control | Expected | Actual | Result |
| --- | --- | --- | --- |
{controls}

## Missing Fields

{missing}

## Boundaries

DataCapsule-2 is a local corpus-manifest receipt. It does not inspect private file contents, crawl directories, fetch URLs, prove legal sufficiency, prove privacy compliance, guarantee data quality, prove evaluation cleanliness, or authorize actions.
"""


def read_manifest_path(path: Path) -> dict[str, Any]:
    resolved = path if path.is_absolute() else _repo_root() / path
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def build_datacapsule2_sample_outputs() -> DataCapsuleCorpusBuildResult:
    _write_json(SAMPLE_MANIFEST_PATH, SAMPLE_CORPUS_MANIFEST)
    result = build_corpus_manifest_result(SAMPLE_CORPUS_MANIFEST, str(SAMPLE_MANIFEST_PATH).replace("\\", "/"))
    _write_json(CAPSULE_PATH, result.capsule.model_dump(mode="json", by_alias=True))
    _write_json(RESULT_PATH, result.model_dump(mode="json", by_alias=True))
    _write_json(NEGATIVE_CONTROL_PATH, {"negative_controls": [item.model_dump(mode="json") for item in result.negative_controls], "false_pass_count": result.negative_control_false_pass_count})
    _write_text(REPORT_PATH, build_corpus_manifest_report(result))
    _write_text(
        NEXT_STEPS_PATH,
        """# DataCapsule-2 Next Steps

1. Add optional CSV/JSONL corpus manifest intake.
2. Add local fixture-based eval-leak separation examples.
3. Keep crawling, legal/privacy certification, and action authorization out of the DataCapsule path.
""",
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a DataCapsule-2 local corpus manifest report.")
    parser.add_argument("--manifest", type=Path, help="Path to a repository-supplied corpus manifest JSON.")
    parser.add_argument("--run-sample", action="store_true", help="Write DataCapsule-2 sample outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.manifest:
        manifest = read_manifest_path(args.manifest)
        result = build_corpus_manifest_result(manifest, str(args.manifest).replace("\\", "/"))
    else:
        result = build_datacapsule2_sample_outputs()
    print(
        "datacapsule2_manifest: "
        f"{result.decision} files={result.summary.file_count} "
        f"negative_control_false_passes={result.negative_control_false_pass_count}"
    )


if __name__ == "__main__":
    main()
