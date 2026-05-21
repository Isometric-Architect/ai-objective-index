from ai_objective_index import private_kernel_template_generator as generator


def test_private_kernel_template_contains_placeholders_only(tmp_path, monkeypatch):
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    monkeypatch.setattr(generator, "_repo_root", lambda: tmp_path)

    result = generator.run_private_kernel_template_generator()
    text = (tmp_path / generator.TEMPLATE_PATH).read_text(encoding="utf-8")

    assert result["placeholder_only"] is True
    assert "Placeholder" in text
    assert "pypi-" not in text


def test_gitignore_contains_private_paths(tmp_path, monkeypatch):
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    monkeypatch.setattr(generator, "_repo_root", lambda: tmp_path)

    generator.run_private_kernel_template_generator()
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")

    assert ".aoi_private/" in text
    assert "private_kernel/" in text
    assert "*.pypirc" in text
