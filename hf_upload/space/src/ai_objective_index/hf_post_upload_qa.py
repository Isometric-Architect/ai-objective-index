from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .hf_auth_check import check_hf_auth


OWNER = "edict-lab"
SPACE_NAME = "ai-objective-index-demo"
DATASET_NAME = "ai-objective-index-sample"
OUTPUT_PATH = Path("huggingface_upload/HF_POST_UPLOAD_QA_RESULT.json")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _api() -> Any:
    from huggingface_hub import HfApi

    return HfApi()


def _repo_exists(api: Any, repo_id: str, repo_type: str) -> tuple[bool, str | None]:
    info = api.repo_info(repo_id=repo_id, repo_type=repo_type)
    visibility = "private" if bool(getattr(info, "private", False)) else "unknown"
    if isinstance(info, dict):
        visibility = "private" if info.get("private") else str(info.get("visibility", "unknown"))
    return True, visibility


def run_hf_post_upload_qa(api: Any | None = None) -> dict[str, Any]:
    space_repo_id = f"{OWNER}/{SPACE_NAME}"
    dataset_repo_id = f"{OWNER}/{DATASET_NAME}"
    space_url = f"https://huggingface.co/spaces/{space_repo_id}"
    dataset_url = f"https://huggingface.co/datasets/{dataset_repo_id}"
    api = api or _api()
    auth = check_hf_auth(api=api, write_result=True)
    authenticated = bool(auth.get("authenticated"))
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "space_url": space_url,
        "dataset_url": dataset_url,
        "space_exists_if_checked": "not_checked",
        "dataset_exists_if_checked": "not_checked",
        "visibility_if_known": "not_checked",
        "build_status_if_available": "not_checked",
        "authenticated": authenticated,
        "qa_token": "NOT_CHECKED",
        "errors": [],
        "warnings": [],
        "next_action": "Authenticate locally or use browser fallback; private repos were not checked.",
        "token_printed": False,
        "actual_upload_performed": False,
        "visibility_changed": False,
    }
    if not authenticated:
        _write_json(OUTPUT_PATH, result)
        return result

    try:
        space_exists, space_visibility = _repo_exists(api, space_repo_id, "space")
        dataset_exists, dataset_visibility = _repo_exists(api, dataset_repo_id, "dataset")
        result["space_exists_if_checked"] = space_exists
        result["dataset_exists_if_checked"] = dataset_exists
        result["visibility_if_known"] = {
            "space": space_visibility,
            "dataset": dataset_visibility,
        }
        try:
            runtime = api.get_space_runtime(space_repo_id)
            result["build_status_if_available"] = getattr(runtime, "stage", None) or str(runtime)
        except Exception:
            result["build_status_if_available"] = "not_available"
        result["qa_token"] = "PASS" if space_exists and dataset_exists else "HOLD"
        result["next_action"] = "Open the private Space/Dataset URLs and test the demo query."
    except Exception as exc:
        result["qa_token"] = "HOLD"
        result["errors"].append(str(exc)[:500])
        result["next_action"] = "Review Hugging Face repo access or use browser fallback."

    _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_hf_post_upload_qa()
    print(
        "hf_post_upload_qa: "
        f"authenticated={result['authenticated']} "
        f"qa_token={result['qa_token']} "
        f"space={result['space_exists_if_checked']} "
        f"dataset={result['dataset_exists_if_checked']}"
    )
    print(f"next_action={result['next_action']}")


if __name__ == "__main__":
    main()
