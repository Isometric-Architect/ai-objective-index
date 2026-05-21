from ai_objective_index import license_ip_positioning_audit as audit


def test_license_present_passes_or_holds_review(tmp_path, monkeypatch):
    (tmp_path / "LICENSE").write_text("MIT License\n\nPermission is hereby granted", encoding="utf-8")
    (tmp_path / "README.md").write_text("License: MIT", encoding="utf-8")
    monkeypatch.setattr(audit, "_repo_root", lambda: tmp_path)

    result = audit.run_license_ip_positioning_audit(write_result=False)

    assert result["decision"] == "PASS_LICENSE_PRESENT"


def test_missing_license_blocks(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text("", encoding="utf-8")
    monkeypatch.setattr(audit, "_repo_root", lambda: tmp_path)

    result = audit.run_license_ip_positioning_audit(write_result=False)

    assert result["decision"] == "BLOCK_LICENSE_MISSING_FOR_PUBLIC_REPO"
