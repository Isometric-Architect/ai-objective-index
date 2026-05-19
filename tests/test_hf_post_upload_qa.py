import ai_objective_index.hf_post_upload_qa as qa


class Info:
    private = True


class FakeApi:
    def repo_info(self, **_kwargs):
        return Info()

    def get_space_runtime(self, _repo_id):
        class Runtime:
            stage = "RUNNING"

        return Runtime()


def test_hf_post_upload_qa_unauthenticated_not_checked(monkeypatch):
    monkeypatch.setattr(qa, "check_hf_auth", lambda **_kwargs: {"authenticated": False})

    result = qa.run_hf_post_upload_qa(api=FakeApi())

    assert result["authenticated"] is False
    assert result["qa_token"] == "NOT_CHECKED"
    assert result["space_exists_if_checked"] == "not_checked"


def test_hf_post_upload_qa_authenticated_fake_api(monkeypatch):
    monkeypatch.setattr(qa, "check_hf_auth", lambda **_kwargs: {"authenticated": True})

    result = qa.run_hf_post_upload_qa(api=FakeApi())

    assert result["authenticated"] is True
    assert result["qa_token"] == "PASS"
    assert result["space_url"].endswith("/edict-lab/ai-objective-index-demo")
    assert result["dataset_url"].endswith("/edict-lab/ai-objective-index-sample")

