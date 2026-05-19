from ai_objective_index import private_deployment_qa as qa


def test_private_deployment_qa_returns_structure(monkeypatch):
    monkeypatch.setattr(qa, "_git", lambda args: {"ok": True, "stdout": "origin https://github.com/Isometric-Architect/ai-objective-index.git"})
    monkeypatch.setattr(
        qa,
        "_read_json",
        lambda path: {
            "huggingface_upload/HF_PRIVATE_UPLOAD_RESULT.json": {
                "space_upload_performed": True,
                "dataset_upload_performed": True,
                "visibility": "private",
            },
            "huggingface_upload/HF_POST_UPLOAD_QA_RESULT.json": {
                "qa_token": "PASS",
                "space_url": qa.HF_SPACE_URL,
                "dataset_url": qa.HF_DATASET_URL,
                "build_status_if_available": "RUNNING",
                "dataset_exists_if_checked": True,
                "visibility_if_known": {"space": "private", "dataset": "private"},
            },
        }.get(str(path), {}),
    )
    result = qa.run_private_deployment_qa(write_result=False)

    assert result["overall_token"] in {"PASS", "HOLD"}
    assert result["public_switch_performed"] is False
    assert result["hf_public_switch_performed"] is False


def test_private_deployment_qa_missing_hf_result_holds(monkeypatch):
    monkeypatch.setattr(qa, "_git", lambda args: {"ok": True, "stdout": "origin https://github.com/Isometric-Architect/ai-objective-index.git"})
    monkeypatch.setattr(qa, "_read_json", lambda path: {})
    result = qa.run_private_deployment_qa(write_result=False)

    assert result["overall_token"] == "HOLD"
    assert result["public_switch_performed"] is False
