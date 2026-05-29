from __future__ import annotations

from datetime import date

from .datacapsule_pilot_receipt import DataCapsuleCorpusManifest


def summarize_staleness_risk(manifest: DataCapsuleCorpusManifest) -> dict:
    value = manifest.declared_update_date
    if not value or value.lower() == "unknown":
        return {
            "status": "HOLD_STALENESS_UNKNOWN",
            "missing_fields": ["declared_update_date"],
            "warnings": ["Update date is unknown from manifest metadata."],
        }
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return {
            "status": "HOLD_STALENESS_UNPARSED",
            "missing_fields": [],
            "warnings": ["Update date is present but not ISO formatted."],
        }
    age_days = (date.today() - parsed).days
    if age_days > 730:
        status = "HOLD_STALENESS_REVIEW"
        warnings = ["Manifest update date is older than two years."]
    else:
        status = "LOW_MANIFEST_RISK"
        warnings = []
    return {
        "status": status,
        "age_days": age_days,
        "missing_fields": [],
        "warnings": warnings,
    }
