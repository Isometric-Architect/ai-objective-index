from ai_objective_index.mcp_registry_failure_classifier import classify_publish_failure, redact_sensitive


def test_classifier_auth_required():
    result = classify_publish_failure(stderr="You must be logged in before publishing", returncode=1, validate_ok=True)

    assert result["classification"] == "AUTH_REQUIRED"


def test_classifier_server_json_invalid():
    result = classify_publish_failure(stderr="validation failed: server returned status 422", returncode=1, validate_ok=False)

    assert result["classification"] == "SERVER_JSON_INVALID"


def test_classifier_already_exists():
    result = classify_publish_failure(stderr="version already exists", returncode=1, validate_ok=True)

    assert result["classification"] == "VERSION_ALREADY_EXISTS"


def test_redacts_token_like_strings():
    text = redact_sensitive("ghp_abcdefghijk pypi-abcdefghijkl")

    assert "ghp_[redacted]" in text
    assert "pypi-[redacted]" in text
