from ai_objective_index.models import ActionObject, ObjectStatus, SourceTrace
from ai_objective_index.scoring import score_object


def _trace(object_id: str, field: str = "pricing") -> SourceTrace:
    return SourceTrace(
        trace_id=f"trace-{object_id}-{field.replace('.', '-')}",
        object_id=object_id,
        field=field,
        source_url="https://example.com/source",
        source_title="Official Source",
        source_snippet="Official source supports this field.",
        retrieved_at="2026-04-28T00:00:00Z",
        confidence=0.9,
    )


def _rich_object(object_id: str = "aoi-rich-image-api") -> ActionObject:
    return ActionObject(
        object_id=object_id,
        name="Rich Image API",
        object_type="api",
        summary="Image generation API with documented pricing, commercial use, rate limits, and quickstart docs.",
        official_url="https://rich.example.com",
        source_urls=["https://rich.example.com/docs", "https://rich.example.com/pricing"],
        capabilities=["text_to_image", "image_generation", "api_access"],
        categories=["image_generation", "creative_api"],
        pricing={
            "model": "usage_based",
            "free_tier": True,
            "starting_price_usd": 10,
            "currency": "USD",
        },
        policies={
            "commercial_use": "Commercial use allowed.",
            "data_retention": "30 days.",
            "rate_limits": "Published by plan.",
            "terms_url": "https://rich.example.com/terms",
            "privacy_url": "https://rich.example.com/privacy",
        },
        docs={
            "docs_url": "https://rich.example.com/docs",
            "api_reference_url": "https://rich.example.com/api",
            "quickstart_url": "https://rich.example.com/start",
        },
        status=ObjectStatus.VERIFIED,
        confidence=0.9,
        missing_fields=[],
        last_checked_at="2026-04-28T00:00:00Z",
    )


def _thin_object(object_id: str = "aoi-thin-image-api") -> ActionObject:
    return ActionObject(
        object_id=object_id,
        name="Thin Image API",
        object_type="api",
        summary="Image tool.",
        official_url=None,
        source_urls=[],
        capabilities=["image_generation"],
        categories=["image_generation"],
        pricing={},
        policies={},
        docs={},
        status=ObjectStatus.UNVERIFIED,
        confidence=0.4,
        missing_fields=["pricing", "docs_url", "commercial_use_terms"],
        last_checked_at=None,
    )


def test_rich_object_scores_higher_than_similar_missing_object():
    rich = _rich_object()
    thin = _thin_object()
    rich_score = score_object(
        rich,
        query="cheap image generation API with commercial use terms",
        traces=[_trace(rich.object_id, "pricing"), _trace(rich.object_id, "policies.commercial_use")],
        constraints={"max_monthly_budget_usd": 50},
    )
    thin_score = score_object(
        thin,
        query="cheap image generation API with commercial use terms",
        traces=[],
        constraints={"max_monthly_budget_usd": 50},
    )

    assert rich_score.objective_score > thin_score.objective_score


def test_stale_or_blocked_object_receives_penalty():
    verified = _rich_object("aoi-verified")
    stale = _rich_object("aoi-stale")
    blocked = _rich_object("aoi-blocked")
    stale.status = ObjectStatus.STALE
    blocked.status = ObjectStatus.BLOCKED

    verified_score = score_object(verified, query="image generation api", traces=[_trace(verified.object_id)])
    stale_score = score_object(stale, query="image generation api", traces=[_trace(stale.object_id)])
    blocked_score = score_object(blocked, query="image generation api", traces=[_trace(blocked.object_id)])

    assert stale_score.penalties["stale_penalty"] > 0
    assert blocked_score.penalties["unsafe_claim_penalty"] > 0
    assert stale_score.objective_score < verified_score.objective_score
    assert blocked_score.objective_score < verified_score.objective_score


def test_result_has_rank_reason_and_unverified_warning():
    thin = _thin_object()

    result = score_object(thin, query="image generation api", traces=[])

    assert result.rank_reason
    assert any("UNVERIFIED" in warning for warning in result.warnings)

