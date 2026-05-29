from __future__ import annotations

from .datacapsule_manifest_summary import stable_id
from .datacapsule_pilot_receipt import DataCapsuleCorpusManifest, DataCapsuleEvalLeakageSummary


def build_eval_leakage_summary(manifest: DataCapsuleCorpusManifest) -> DataCapsuleEvalLeakageSummary:
    missing: list[str] = []
    warnings: list[str] = []
    overlap = manifest.declared_eval_overlap_status
    contamination = "unknown"
    split_policy = "unknown"
    if overlap == "unknown":
        missing.append("declared_eval_overlap_status")
    if split_policy == "unknown":
        missing.append("split_policy")
    if overlap == "present" or contamination == "present":
        status = "BLOCK_DECLARED_EVAL_CONTAMINATION"
        warnings.append("Manifest declares evaluation overlap or benchmark contamination.")
    elif overlap == "unknown":
        status = "HOLD_EVAL_OVERLAP_UNKNOWN"
        warnings.append("Evaluation overlap is unknown from manifest metadata.")
    elif split_policy == "unknown":
        status = "HOLD_SPLIT_POLICY_MISSING"
        warnings.append("Train/eval split policy is not declared.")
    else:
        status = "LOW_MANIFEST_RISK"
    return DataCapsuleEvalLeakageSummary(
        summary_id=stable_id("datacapsule-eval", manifest.manifest_id, overlap, split_policy),
        manifest_id=manifest.manifest_id,
        eval_overlap_declared=overlap,
        benchmark_contamination_declared=contamination,  # type: ignore[arg-type]
        split_policy_declared=split_policy,  # type: ignore[arg-type]
        leakage_status=status,  # type: ignore[arg-type]
        missing_fields=missing,
        warnings=warnings,
    )
