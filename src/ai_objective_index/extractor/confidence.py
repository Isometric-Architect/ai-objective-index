from __future__ import annotations

from ai_objective_index.models import SourceRank
from ai_objective_index.source_trace import source_rank_to_weight


def source_rank_for_page_type(page_type: str) -> SourceRank:
    return {
        "pricing": SourceRank.S,
        "api_reference": SourceRank.S,
        "docs": SourceRank.A,
        "terms": SourceRank.S,
        "privacy": SourceRank.S,
        "github_readme": SourceRank.A,
        "homepage": SourceRank.B,
        "faq": SourceRank.C,
    }.get(page_type, SourceRank.UNKNOWN)


def confidence_from_source(
    page_type: str,
    source_rank: SourceRank | str,
    keyword_strength: float,
    field_presence: bool,
) -> float:
    base = source_rank_to_weight(source_rank) * 0.65
    page_bonus = {
        "pricing": 0.15,
        "api_reference": 0.15,
        "docs": 0.12,
        "terms": 0.15,
        "privacy": 0.15,
        "github_readme": 0.12,
        "homepage": 0.05,
    }.get(page_type, 0.02)
    presence_bonus = 0.12 if field_presence else 0.0
    strength_bonus = max(0.0, min(1.0, keyword_strength)) * 0.08
    return round(max(0.0, min(1.0, base + page_bonus + presence_bonus + strength_bonus)), 3)

