import json

import ai_objective_index.hf_private_upload as upload


class FakeApi:
    def __init__(self):
        self.created = []
        self.uploaded = []

    def whoami(self):
        return {"name": "edict-lab"}

    def create_repo(self, **kwargs):
        self.created.append(kwargs)
        return {"ok": True}

    def upload_folder(self, **kwargs):
        self.uploaded.append(kwargs)
        return {"ok": True}


def test_hf_private_upload_dry_run_does_not_upload():
    result = upload.run_hf_private_upload(execute=False)

    assert result["dry_run"] is True
    assert result["space_upload_performed"] is False
    assert result["dataset_upload_performed"] is False
    assert result["token_printed"] is False


def test_hf_private_upload_execute_without_auth_stops(monkeypatch):
    monkeypatch.setattr(upload, "check_hf_auth", lambda **_kwargs: {"authenticated": False})

    result = upload.run_hf_private_upload(execute=True, api=FakeApi())

    assert result["authenticated"] is False
    assert result["actual_upload_performed"] is False
    assert result["space_upload_performed"] is False
    assert "Do not paste tokens" in result["next_action"]


def test_hf_private_upload_execute_with_fake_api_uploads():
    fake = FakeApi()
    result = upload.run_hf_private_upload(execute=True, api=fake)

    text = json.dumps(result).lower()
    assert result["authenticated"] is True
    assert result["space_created_or_exists"] is True
    assert result["dataset_created_or_exists"] is True
    assert result["space_upload_performed"] is True
    assert result["dataset_upload_performed"] is True
    assert "hf_fake_token" not in text
    assert "secret" not in text
    assert all(item.get("private") is True for item in fake.created)
