"""DataCapsule local metadata MVP.

DataCapsule converts repository-supplied data/corpus metadata into local use
boundary capsules and corpus-manifest reports. It does not crawl, fetch URLs,
inspect private data, make legal/privacy compliance claims, or authorize actions.
"""

from .capsule_builder import (
    SAMPLE_DATASET_METADATA,
    build_datacapsule_report,
    build_datacapsule_sample_outputs,
    build_datacapsule_from_metadata,
    read_metadata_path,
)
from .models import (
    CorpusManifestSummary,
    DataCapsule,
    DataCapsuleBuildResult,
    DataCapsuleCorpusBuildResult,
    DataCapsuleNegativeControl,
    DataUseBoundary,
    DataUsePermission,
    RiskFlags,
)

__all__ = [
    "DataCapsule",
    "DataCapsuleBuildResult",
    "DataCapsuleCorpusBuildResult",
    "DataCapsuleNegativeControl",
    "DataUseBoundary",
    "DataUsePermission",
    "CorpusManifestSummary",
    "RiskFlags",
    "SAMPLE_DATASET_METADATA",
    "build_datacapsule_report",
    "build_datacapsule_sample_outputs",
    "build_datacapsule_from_metadata",
    "read_metadata_path",
]
