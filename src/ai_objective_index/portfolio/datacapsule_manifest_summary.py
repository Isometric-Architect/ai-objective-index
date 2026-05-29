from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .datacapsule_pilot_receipt import DataCapsuleCorpusManifest, OwnerConsent


SAMPLE_MANIFEST = {
    "corpus_label": "DataCapsule local sample corpus",
    "source_type": "sample_fixture",
    "data_categories": ["text", "metadata"],
    "declared_sources": ["repository-local sample manifest"],
    "declared_license": "unknown",
    "declared_terms": "unknown",
    "declared_collection_method": "unknown",
    "declared_update_date": "unknown",
    "declared_pii_status": "unknown",
    "declared_eval_overlap_status": "unknown",
    "declared_allowed_uses": ["retrieve"],
    "declared_disallowed_uses": ["act"],
    "declared_retention_policy": "unknown",
    "declared_share_policy": "unknown",
}


def stable_id(prefix: str, *parts: object) -> str:
    text = "::".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def load_manifest_payload(input_path: Path | None = None) -> dict[str, Any]:
    if input_path is None:
        return dict(SAMPLE_MANIFEST)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("DataCapsule pilot manifest must be a JSON object.")
    return payload


def build_corpus_manifest(payload: dict[str, Any], owner_status: str = "sample_fixture") -> DataCapsuleCorpusManifest:
    manifest_id = stable_id("datacapsule-manifest", payload.get("corpus_label", ""), payload.get("declared_sources", []))
    return DataCapsuleCorpusManifest(
        manifest_id=manifest_id,
        corpus_label=str(payload.get("corpus_label") or "DataCapsule local manifest"),
        owner_consent=OwnerConsent(status=owner_status, evidence_note="manifest metadata supplied locally; no external owner contacted"),
        source_type=str(payload.get("source_type") or "sample_fixture"),  # type: ignore[arg-type]
        data_categories=[str(item) for item in payload.get("data_categories", ["unknown"])],  # type: ignore[list-item]
        declared_sources=[str(item) for item in payload.get("declared_sources", [])],
        declared_license=str(payload.get("declared_license") or "unknown"),
        declared_terms=str(payload.get("declared_terms") or "unknown"),
        declared_collection_method=str(payload.get("declared_collection_method") or "unknown"),
        declared_update_date=str(payload.get("declared_update_date") or "unknown"),
        declared_pii_status=str(payload.get("declared_pii_status") or "unknown"),  # type: ignore[arg-type]
        declared_eval_overlap_status=str(payload.get("declared_eval_overlap_status") or "unknown"),  # type: ignore[arg-type]
        declared_allowed_uses=[str(item) for item in payload.get("declared_allowed_uses", [])],
        declared_disallowed_uses=[str(item) for item in payload.get("declared_disallowed_uses", [])],
        declared_retention_policy=str(payload.get("declared_retention_policy") or "unknown"),
        declared_share_policy=str(payload.get("declared_share_policy") or "unknown"),
        local_manifest_only=True,
        raw_content_inspected=False,
        external_network_used=False,
    )
