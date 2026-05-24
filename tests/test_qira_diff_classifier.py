from ai_objective_index.qira.diff_classifier import classify_changed_file, classify_patch_paths


def test_classify_common_paths():
    assert classify_changed_file("src/app.py").category == "source"
    assert classify_changed_file("tests/test_app.py").category == "test"
    assert classify_changed_file("docs/readme.md").category == "docs"
    assert classify_changed_file(".github/workflows/ci.yml").category == "ci"


def test_classify_private_and_escape_paths_block():
    secret = classify_changed_file(".env")
    escaped = classify_changed_file("../outside.py")

    assert secret.risk == "BLOCK"
    assert secret.category == "private_or_secret"
    assert escaped.risk == "BLOCK"
    assert escaped.category == "path_escape"


def test_classify_patch_paths_from_diff_holds_dependency_change():
    diff = """diff --git a/pyproject.toml b/pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
"""

    report = classify_patch_paths(patch_diff=diff)

    assert report.decision == "HOLD_PATH_REVIEW"
    assert report.category_counts["dependency"] == 1
    assert report.external_actions_performed is False


def test_classify_patch_paths_without_files_holds():
    report = classify_patch_paths()

    assert report.decision == "HOLD_NO_CHANGED_FILES"
    assert report.patch_applied is False
