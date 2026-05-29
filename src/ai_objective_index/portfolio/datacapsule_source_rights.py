from __future__ import annotations

from .datacapsule_manifest_summary import stable_id
from .datacapsule_pilot_receipt import DataCapsuleCorpusManifest, DataCapsuleSourceRightsSummary


def _known(value: str) -> bool:
    return bool(value and value.strip() and value.strip().lower() not in {"unknown", "none", "n/a"})


def build_source_rights_summary(manifest: DataCapsuleCorpusManifest) -> DataCapsuleSourceRightsSummary:
    missing: list[str] = []
    warnings: list[str] = []
    license_found = _known(manifest.declared_license)
    terms_found = _known(manifest.declared_terms)
    source_found = bool(manifest.declared_sources)
    method_found = _known(manifest.declared_collection_method)
    if not license_found:
        missing.append("declared_license")
    if not terms_found:
        missing.append("declared_terms")
    if not source_found:
        missing.append("declared_sources")
    if not method_found:
        missing.append("declared_collection_method")

    disallowed = {item.lower() for item in manifest.declared_disallowed_uses}
    allowed = {item.lower() for item in manifest.declared_allowed_uses}
    if {"train", "retrieve", "evaluate", "share", "commercial"} & disallowed:
        status = "BLOCK_DISALLOWED_USE_DECLARED"
        warnings.append("Manifest explicitly disallows one or more reviewed use classes.")
    elif not license_found:
        status = "HOLD_LICENSE_MISSING"
        warnings.append("License field is missing or unknown.")
    elif missing:
        status = "HOLD_RIGHTS_UNCLEAR"
        warnings.append("Source or terms fields are incomplete.")
    else:
        status = "SOURCE_RIGHTS_DECLARED"

    return DataCapsuleSourceRightsSummary(
        summary_id=stable_id("datacapsule-rights", manifest.manifest_id, manifest.declared_license, manifest.declared_terms),
        manifest_id=manifest.manifest_id,
        license_found=license_found,
        terms_found=terms_found,
        source_attribution_found=source_found,
        collection_method_found=method_found,
        redistribution_allowed_declared=True if "share" in allowed else False if "share" in disallowed else None,
        training_allowed_declared=True if "train" in allowed else False if "train" in disallowed else None,
        retrieval_allowed_declared=True if "retrieve" in allowed else False if "retrieve" in disallowed else None,
        evaluation_allowed_declared=True if "evaluate" in allowed else False if "evaluate" in disallowed else None,
        commercial_use_declared=True if "commercial" in allowed else False if "commercial" in disallowed else None,
        rights_status=status,  # type: ignore[arg-type]
        missing_fields=missing,
        warnings=warnings,
    )
