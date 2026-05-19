from ai_objective_index import hf_github_crosslink_audit as audit


def _target(name: str):
    return audit._repo_root() / "tests" / name


def test_crosslink_audit_detects_missing_links():
    target = _target("__tmp_8h_missing_links.md")
    try:
        target.write_text("Private deployment only.\n", encoding="utf-8")
        result = audit.audit_crosslinks(files=[target], write_result=False)

        assert result["overall_token"] == "HOLD"
        assert result["missing_links"]
    finally:
        if target.exists():
            target.unlink()


def test_crosslink_audit_detects_positive_public_claim():
    target = _target("__tmp_8h_public_claim.md")
    try:
        target.write_text(
            f"GitHub private repo: {audit.GITHUB_URL}\n"
            f"Hugging Face Space, private: {audit.HF_SPACE_URL}\n"
            f"Hugging Face Dataset, private: {audit.HF_DATASET_URL}\n"
            "The public release is complete.\n",
            encoding="utf-8",
        )

        result = audit.audit_crosslinks(files=[target], write_result=False)

        assert result["overall_token"] == "HOLD"
        assert result["risky_phrase_count"] > 0
    finally:
        if target.exists():
            target.unlink()


def test_crosslink_audit_passes_private_wording():
    target = _target("__tmp_8h_private_wording.md")
    try:
        target.write_text(
            f"GitHub private repo: {audit.GITHUB_URL}\n"
            f"Hugging Face Space, private: {audit.HF_SPACE_URL}\n"
            f"Hugging Face Dataset, private: {audit.HF_DATASET_URL}\n"
            "Not verified, not security certified, not a quality guarantee.\n",
            encoding="utf-8",
        )

        result = audit.audit_crosslinks(files=[target], write_result=False)

        assert result["overall_token"] == "PASS"
    finally:
        if target.exists():
            target.unlink()
