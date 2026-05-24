from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root, _write_json

from .corpus_manifest import build_corpus_manifest_report, build_corpus_manifest_result
from .eval_leak import build_eval_leak_separation_report
from .models import DataCapsuleManifestIntakeResult


OUTPUT_DIR = Path("public_launch") / "datacapsule3"
SAMPLE_CSV_PATH = OUTPUT_DIR / "DATACAPSULE3_SAMPLE_MANIFEST.csv"
SAMPLE_JSONL_PATH = OUTPUT_DIR / "DATACAPSULE3_SAMPLE_MANIFEST.jsonl"
NORMALIZED_MANIFEST_PATH = OUTPUT_DIR / "DATACAPSULE3_NORMALIZED_MANIFEST.json"
CORPUS_CAPSULE_PATH = OUTPUT_DIR / "DATACAPSULE3_CORPUS_CAPSULE.json"
CORPUS_RESULT_PATH = OUTPUT_DIR / "DATACAPSULE3_CORPUS_RESULT.json"
EVAL_LEAK_REPORT_PATH = OUTPUT_DIR / "DATACAPSULE3_EVAL_LEAK_SEPARATION_REPORT.json"
REPORT_PATH = OUTPUT_DIR / "DATACAPSULE3_REPORT.md"
RESULT_PATH = OUTPUT_DIR / "DATACAPSULE3_RESULT.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "DATACAPSULE3_NEXT_STEPS.md"


SAMPLE_CSV_TEXT = """path,source,license,privacy_level,purpose,risk_flags
docs/rag-guide.md,repository-local-doc,MIT,public_metadata,"retrieve;summarize",
docs/eval-set.md,repository-local-eval,MIT,public_metadata,evaluate,
docs/train-notes.md,repository-local-train,MIT,public_metadata,train,
"""

SAMPLE_JSONL_TEXT = "\n".join(
    [
        json.dumps(
            {
                "path": "docs/rag-guide.md",
                "source": "repository-local-doc",
                "license": "MIT",
                "privacy_level": "public_metadata",
                "purpose": ["retrieve", "summarize"],
            }
        ),
        json.dumps(
            {
                "path": "docs/eval-set.md",
                "source": "repository-local-eval",
                "license": "MIT",
                "privacy_level": "public_metadata",
                "purpose": ["evaluate"],
            }
        ),
        json.dumps(
            {
                "path": "docs/train-notes.md",
                "source": "repository-local-train",
                "license": "MIT",
                "privacy_level": "public_metadata",
                "purpose": ["train"],
            }
        ),
    ]
) + "\n"


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8", newline="")
    return destination


def _purpose(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]
    return []


def _risk_flags(value: Any) -> dict[str, bool]:
    if isinstance(value, dict):
        return {str(key): bool(child) for key, child in value.items()}
    if not isinstance(value, str) or not value.strip():
        return {}
    flags: dict[str, bool] = {}
    for part in value.replace(";", ",").split(","):
        key = part.strip()
        if key:
            flags[key] = True
    return flags


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": str(row.get("path") or "").strip(),
        "source": str(row.get("source") or "").strip(),
        "license": str(row.get("license") or "unknown").strip() or "unknown",
        "privacy_level": str(row.get("privacy_level") or "unknown").strip() or "unknown",
        "purpose": _purpose(row.get("purpose")),
        "risk_flags": _risk_flags(row.get("risk_flags")),
    }


def read_csv_manifest(path: Path) -> list[dict[str, Any]]:
    resolved = path if path.is_absolute() else _repo_root() / path
    with resolved.open("r", encoding="utf-8", newline="") as handle:
        return [_normalize_row(row) for row in csv.DictReader(handle)]


def read_jsonl_manifest(path: Path) -> list[dict[str, Any]]:
    resolved = path if path.is_absolute() else _repo_root() / path
    rows: list[dict[str, Any]] = []
    for line in resolved.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(_normalize_row(payload))
    return rows


def rows_to_corpus_manifest(rows: list[dict[str, Any]], corpus_id: str, name: str, source_format: str) -> dict[str, Any]:
    purposes = {purpose for row in rows for purpose in _purpose(row.get("purpose"))}
    return {
        "corpus_id": corpus_id,
        "name": name,
        "root_path": "",
        "source": f"repository-local-{source_format}-manifest",
        "allowed_use": {
            "train": "train" in purposes,
            "retrieve": "retrieve" in purposes,
            "evaluate": "evaluate" in purposes or "eval" in purposes,
            "summarize": "summarize" in purposes,
            "share": False,
            "act": False,
        },
        "files": rows,
        "claim_boundaries": [
            "not legal sufficiency",
            "not privacy compliance",
            "not data quality guarantee",
            "no action authorization",
        ],
    }


def load_manifest_table(path: Path) -> tuple[str, list[dict[str, Any]]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv", read_csv_manifest(path)
    if suffix == ".jsonl":
        return "jsonl", read_jsonl_manifest(path)
    if suffix == ".json":
        resolved = path if path.is_absolute() else _repo_root() / path
        payload = json.loads(resolved.read_text(encoding="utf-8"))
        files = payload.get("files") if isinstance(payload, dict) else []
        return "json", [_normalize_row(row) for row in files if isinstance(row, dict)]
    raise ValueError(f"unsupported manifest format: {suffix}")


def _result_decision(corpus_decision: str, eval_decision: str) -> str:
    if corpus_decision.startswith("BLOCK") or eval_decision.startswith("BLOCK"):
        return "BLOCK_DATACAPSULE3_USE_RISK"
    if corpus_decision.startswith("HOLD") or eval_decision.startswith("HOLD"):
        return "HOLD_DATACAPSULE3_REVIEW_REQUIRED"
    return "PASS_DATACAPSULE3_MANIFEST_INTAKE"


def build_manifest_intake_result(
    path: Path,
    corpus_id: str,
    name: str,
    normalized_manifest_path: Path = NORMALIZED_MANIFEST_PATH,
    corpus_capsule_path: Path = CORPUS_CAPSULE_PATH,
    corpus_result_path: Path = CORPUS_RESULT_PATH,
    eval_leak_report_path: Path = EVAL_LEAK_REPORT_PATH,
    report_path: Path = REPORT_PATH,
) -> DataCapsuleManifestIntakeResult:
    source_format, rows = load_manifest_table(path)
    manifest = rows_to_corpus_manifest(rows, corpus_id=corpus_id, name=name, source_format=source_format)
    corpus_result = build_corpus_manifest_result(
        manifest,
        str(path).replace("\\", "/"),
        capsule_path=corpus_capsule_path,
        report_path=report_path,
    )
    eval_report = build_eval_leak_separation_report(manifest)
    return DataCapsuleManifestIntakeResult(
        result_id=f"datacapsule3-{corpus_result.result_id.removeprefix('datacapsule2-')}",
        decision=_result_decision(corpus_result.decision, eval_report.decision),
        source_format=source_format,
        source_path=str(path).replace("\\", "/"),
        normalized_manifest_path=str(normalized_manifest_path).replace("\\", "/"),
        corpus_result_path=str(corpus_result_path).replace("\\", "/"),
        eval_leak_report_path=str(eval_leak_report_path).replace("\\", "/"),
        corpus_result=corpus_result,
        eval_leak_report=eval_report,
        known_limits=[
            "local CSV/JSONL/JSON manifest metadata only",
            "no directory crawling",
            "no private file content inspection",
            "no URL fetch",
            "not legal sufficiency",
            "not privacy compliance",
            "not data quality guarantee",
            "not evaluation cleanliness proof",
            "not action authorization",
        ],
    )


def build_manifest_intake_report(result: DataCapsuleManifestIntakeResult) -> str:
    return f"""# DataCapsule-3 Manifest Intake Report

Decision: `{result.decision}`

| Field | Value |
| --- | --- |
| Source format | `{result.source_format}` |
| Source path | `{result.source_path}` |
| File count | `{result.corpus_result.summary.file_count}` |
| Eval separation | `{result.eval_leak_report.decision}` |
| Eval/train overlap count | `{result.eval_leak_report.overlap_count}` |
| Negative-control false passes | `{result.corpus_result.negative_control_false_pass_count}` |
| Network used | `False` |
| Crawler used | `False` |
| External service used | `False` |

## Boundaries

DataCapsule-3 normalizes local manifest metadata only. It does not crawl directories, inspect private file contents, fetch URLs, prove legal sufficiency, prove privacy compliance, guarantee data quality, prove evaluation cleanliness, or authorize actions.
"""


def build_datacapsule3_sample_outputs(use_jsonl: bool = False) -> DataCapsuleManifestIntakeResult:
    sample_path = SAMPLE_JSONL_PATH if use_jsonl else SAMPLE_CSV_PATH
    _write_text(SAMPLE_CSV_PATH, SAMPLE_CSV_TEXT)
    _write_text(SAMPLE_JSONL_PATH, SAMPLE_JSONL_TEXT)
    result = build_manifest_intake_result(
        sample_path,
        corpus_id="fixture.local/datacapsule3-corpus",
        name="DataCapsule-3 local manifest fixture",
    )
    _write_json(NORMALIZED_MANIFEST_PATH, rows_to_corpus_manifest(load_manifest_table(sample_path)[1], "fixture.local/datacapsule3-corpus", "DataCapsule-3 local manifest fixture", result.source_format))
    _write_json(CORPUS_CAPSULE_PATH, result.corpus_result.capsule.model_dump(mode="json", by_alias=True))
    _write_json(CORPUS_RESULT_PATH, result.corpus_result.model_dump(mode="json", by_alias=True))
    _write_json(EVAL_LEAK_REPORT_PATH, result.eval_leak_report.model_dump(mode="json", by_alias=True))
    _write_json(RESULT_PATH, result.model_dump(mode="json", by_alias=True))
    _write_text(REPORT_PATH, build_manifest_intake_report(result))
    _write_text(
        NEXT_STEPS_PATH,
        """# DataCapsule-3 Next Steps

1. Add optional repository CI artifact bridge for corpus manifests.
2. Add local RAG corpus policy profiles.
3. Keep live crawling, rights/privacy certification, and action authorization outside DataCapsule.
""",
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize CSV/JSONL corpus manifests into DataCapsule-3 reports.")
    parser.add_argument("--manifest", type=Path, help="Path to a local CSV, JSONL, or JSON corpus manifest.")
    parser.add_argument("--corpus-id", default="fixture.local/datacapsule3-corpus")
    parser.add_argument("--name", default="DataCapsule-3 local manifest")
    parser.add_argument("--run-sample", action="store_true")
    parser.add_argument("--sample-jsonl", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.manifest:
        result = build_manifest_intake_result(args.manifest, corpus_id=args.corpus_id, name=args.name)
    else:
        result = build_datacapsule3_sample_outputs(use_jsonl=args.sample_jsonl)
    print(
        "datacapsule3_intake: "
        f"{result.decision} format={result.source_format} files={result.corpus_result.summary.file_count} "
        f"eval_decision={result.eval_leak_report.decision}"
    )


if __name__ == "__main__":
    main()
