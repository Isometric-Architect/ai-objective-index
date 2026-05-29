from __future__ import annotations

from .datacapsule_manifest_summary import stable_id
from .datacapsule_pilot_receipt import DataCapsuleCorpusManifest, DataCapsulePrivacyRiskSummary


def build_privacy_risk_summary(manifest: DataCapsuleCorpusManifest) -> DataCapsulePrivacyRiskSummary:
    missing: list[str] = []
    warnings: list[str] = []
    pii = manifest.declared_pii_status
    sensitive = "unknown"
    deid = "unknown"
    consent = "unknown"
    if pii == "unknown":
        missing.append("declared_pii_status")
    if manifest.declared_retention_policy.lower() == "unknown":
        missing.append("declared_retention_policy")
    if pii == "present" or sensitive == "present":
        status = "BLOCK_DECLARED_SENSITIVE_DATA"
        warnings.append("Manifest declares sensitive or PII-bearing data.")
    elif pii == "unknown":
        status = "HOLD_PII_UNKNOWN"
        warnings.append("PII status is unknown from manifest metadata.")
    elif consent == "unknown":
        status = "HOLD_CONSENT_UNKNOWN"
        warnings.append("Consent status is not declared in the manifest.")
    elif deid == "unknown":
        status = "HOLD_DEIDENTIFICATION_UNKNOWN"
        warnings.append("Deidentification status is not declared in the manifest.")
    else:
        status = "LOW_MANIFEST_RISK"
    return DataCapsulePrivacyRiskSummary(
        summary_id=stable_id("datacapsule-privacy", manifest.manifest_id, pii, manifest.declared_retention_policy),
        manifest_id=manifest.manifest_id,
        pii_declared=pii,
        sensitive_data_declared=sensitive,  # type: ignore[arg-type]
        deidentification_declared=deid,  # type: ignore[arg-type]
        consent_declared=consent,  # type: ignore[arg-type]
        privacy_status=status,  # type: ignore[arg-type]
        missing_fields=missing,
        warnings=warnings,
    )
