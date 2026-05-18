from ai_objective_index.extractor.page_classifier import classify_page


def test_pricing_url_or_text_classified_as_pricing() -> None:
    assert classify_page("https://example.com/pricing", text="Free plan and paid tiers") == "pricing"


def test_docs_url_or_text_classified_as_docs() -> None:
    assert classify_page("https://example.com/docs", text="Documentation quickstart") == "docs"


def test_github_readme_classified_as_github_readme() -> None:
    assert (
        classify_page(
            "https://github.com/example/tool/blob/main/README.md",
            title="README",
            text="# Tool",
        )
        == "github_readme"
    )

