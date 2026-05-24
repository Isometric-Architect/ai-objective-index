"""DataCapsule local metadata MVP.

DataCapsule-1 converts repository-supplied data/corpus metadata into local use
boundary capsules. It does not crawl, fetch URLs, inspect private data, make
legal/privacy compliance claims, or authorize actions.
"""

from .capsule_builder import (
    SAMPLE_DATASET_METADATA,
    build_datacapsule_report,
    build_datacapsule_sample_outputs,
    build_datacapsule_from_metadata,
    read_metadata_path,
)
from .models import DataCapsule, DataCapsuleBuildResult, DataUseBoundary, DataUsePermission, RiskFlags

__all__ = [
    "DataCapsule",
    "DataCapsuleBuildResult",
    "DataUseBoundary",
    "DataUsePermission",
    "RiskFlags",
    "SAMPLE_DATASET_METADATA",
    "build_datacapsule_report",
    "build_datacapsule_sample_outputs",
    "build_datacapsule_from_metadata",
    "read_metadata_path",
]
