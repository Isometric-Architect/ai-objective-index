from ai_objective_index.crawler.robots_policy import is_allowed, parse_robots_txt


def test_robots_disallow_path_blocks() -> None:
    robots = "User-agent: *\nDisallow: /private\n"

    assert not is_allowed("https://example.com/private/page", "AI-Objective-Index-Bot/0.1", robots)


def test_robots_allowed_path_passes() -> None:
    robots = "User-agent: *\nDisallow: /private\n"

    assert is_allowed("https://example.com/public/page", "AI-Objective-Index-Bot/0.1", robots)


def test_missing_robots_is_conservative() -> None:
    assert not is_allowed("https://example.com/public/page", "AI-Objective-Index-Bot/0.1", None)


def test_parse_robots_txt_supports_user_agent() -> None:
    parsed = parse_robots_txt("User-agent: AOI\nDisallow: /blocked\n")

    assert parsed["aoi"] == ["/blocked"]

