from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


HF_OWNER = "edict-lab"
SPACE_NAME = "ai-objective-index-demo"
DATASET_NAME = "ai-objective-index-sample"
UPLOAD_ROOT = Path("hf_upload")


SPACE_APP = r'''from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import gradio as gr
except Exception:
    gr = None


def _ensure_src_import() -> None:
    import sys

    root = Path(__file__).resolve().parent
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


_ensure_src_import()

from ai_objective_index.mcp_tools import get_source_trace, search_objectives  # noqa: E402


SCOPES = ["public_beta_mcp", "sample", "mcp_registry", "integrated", "generated", "curated", "public_beta"]


def _default_scope() -> str:
    dataset = Path("data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json")
    if dataset.exists():
        try:
            payload = json.loads(dataset.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if int(payload.get("beta_candidate_count", 0) or 0) > 0:
            return "public_beta_mcp"
    return "sample"


def _safe_data_scope(data_scope: str | None) -> str:
    value = (data_scope or _default_scope()).strip().lower()
    return value if value in SCOPES else _default_scope()


def run_demo_query(
    query: str,
    objective: str = "",
    limit: int = 5,
    data_scope: str | None = None,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    safe_query = (query or "").strip() or "browser automation MCP server"
    scope = _safe_data_scope(data_scope)
    result = search_objectives(
        query=safe_query,
        objective=objective or None,
        limit=max(1, int(limit or 5)),
        data_scope=scope,
    )
    rows: list[dict[str, Any]] = []
    source_trace_preview: dict[str, Any] = {}
    for item in result.get("results", []):
        rows.append(
            {
                "object_id": item.get("object_id"),
                "name": item.get("name"),
                "type": item.get("object_type"),
                "score": item.get("objective_score"),
                "status": item.get("display_status") or item.get("status"),
                "missing_fields": ", ".join(item.get("missing_fields", [])[:4]),
            }
        )
    if rows:
        source_trace_preview = get_source_trace(rows[0]["object_id"], data_scope=scope)

    warning = (
        "public_beta_mcp candidates are registry metadata candidates, not verified, "
        "not security certified, not quality guaranteed, and not action-ready."
        if scope == "public_beta_mcp"
        else "Read-only local benchmark data. Not a quality guarantee or purchasing advice."
    )
    top = rows[0] if rows else {}
    summary = "\n".join(
        [
            "## AI Objective Index HF Demo",
            "",
            warning,
            "",
            f"Query: `{safe_query}`",
            f"Data scope: `{scope}`",
            f"Top result: `{top.get('name', 'none')}`",
            f"Objective score: `{top.get('score', 'n/a')}`",
            f"Warnings: `{'; '.join(result.get('warnings', [])) or 'none'}`",
        ]
    )
    payload = {
        "read_only": True,
        "data_scope": scope,
        "limitations": [
            "not verified",
            "not security certified",
            "not quality guarantee",
            "no purchasing advice",
            "no payment, booking, login, email, purchase, or contract execution",
        ],
        "query_result": result,
        "source_trace_preview": source_trace_preview,
    }
    return summary, rows, payload


def build_demo():
    if gr is None:
        return None
    with gr.Blocks(title="AI Objective Index") as demo:
        gr.Markdown(
            "# AI Objective Index\n"
            "Read-only objective-fit ranking for AI tools/APIs/SaaS/MCP servers.\n\n"
            "`public_beta_mcp` contains Official MCP Registry metadata candidates, not verified or security certified tools."
        )
        query = gr.Textbox(label="Query", value="browser automation MCP server")
        objective = gr.Textbox(label="Objective", value="source-traced MCP server comparison")
        limit = gr.Slider(label="Limit", minimum=1, maximum=10, step=1, value=5)
        data_scope = gr.Dropdown(label="Data scope", choices=SCOPES, value=_default_scope())
        run = gr.Button("Run read-only query")
        summary = gr.Markdown()
        table = gr.Dataframe(label="Results", interactive=False)
        output = gr.JSON(label="JSON output")
        run.click(run_demo_query, inputs=[query, objective, limit, data_scope], outputs=[summary, table, output])
    return demo


def main() -> None:
    if gr is None:
        print("Install gradio to run the Hugging Face demo locally.")
        summary, rows, payload = run_demo_query("browser automation MCP server")
        print(summary)
        print(json.dumps({"rows": rows[:2], "read_only": payload["read_only"]}, indent=2))
        return
    build_demo().launch()


if __name__ == "__main__":
    main()
'''


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ignore_copy(_dir: str, names: list[str]) -> set[str]:
    ignored = {
        "__pycache__",
        ".pytest_cache",
        ".git",
        ".env",
        ".env.local",
        "source_cache",
    }
    return {name for name in names if name in ignored or name.endswith(".pyc")}


def _copy_file(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _copy_tree(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=_ignore_copy)
    return True


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip())


def _space_readme() -> str:
    return f"""---
title: AI Objective Index Demo
colorFrom: blue
colorTo: gray
sdk: gradio
app_file: app.py
pinned: false
---

# AI Objective Index HF Space Demo

This is a manual-upload Hugging Face Space bundle for AI Objective Index.

It runs a read-only Gradio demo over local AOI data. The default scope is `public_beta_mcp` when registry metadata candidates are available, otherwise `sample`.

## Run

Hugging Face should run:

```bash
python app.py
```

## Boundary

`public_beta_mcp` contains Official MCP Registry metadata candidates. They are not verified, not security certified, not a quality guarantee, not purchasing advice, and not action-ready.

The demo does not crawl, fetch live network data, log in, send email, submit forms, buy, book, purchase, connect accounts, verify suppliers, or sign contracts.

## Private Deployment Links

- GitHub private staging repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- MCP Registry submission: HOLD, manual only.

These links are private deployment links unless the owner manually changes visibility. They are not a public release claim.
"""


def _dataset_readme() -> str:
    return f"""# Dataset Card: {DATASET_NAME}

## Summary

This manual-upload dataset bundle contains AI Objective Index sample benchmark data and `public_beta_mcp` Official MCP Registry metadata candidates.

## Files

- `action_objects.jsonl`
- `source_traces.jsonl`
- `objective_scores.jsonl`
- `golden_queries.jsonl`
- `eval_results.json`
- `mcp_registry_beta_candidates.jsonl`
- `mcp_registry_source_traces.jsonl`
- `public_beta_mcp_dataset.json`

## Intended Use

Read-only benchmark testing for objective ranking and source-traced comparison of AI tools, APIs, SaaS products, and MCP servers.

## Claim Boundary

The registry candidates are not verified, not security certified, not a quality guarantee, and not purchasing advice. Source traces support fields but do not prove completeness, currentness, legality, security, or quality.

No payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract execution is included.

## Private Deployment Links

- GitHub private staging repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- MCP Registry submission: HOLD, manual only.

These links are private deployment links unless the owner manually changes visibility. They are not a public release claim.
"""


def _space_steps() -> str:
    return f"""# Hugging Face Space Upload Steps

1. Go to Hugging Face.
2. Click **New > Space**.
3. Owner: `{HF_OWNER}`.
4. Space name: `{SPACE_NAME}`.
5. SDK: **Gradio**.
6. Visibility: **Private first**.
7. Create Space.
8. Open **Files and versions**.
9. Upload all files from `hf_upload/space`.
10. Wait for build.
11. Test a sample query such as `browser automation MCP server`.
12. Do not add tokens or secrets.

If the Space fails to build, copy the build log and ask Codex/ChatGPT for help.
"""


def _dataset_steps() -> str:
    return f"""# Hugging Face Dataset Upload Steps

1. Click **New > Dataset**.
2. Owner: `{HF_OWNER}`.
3. Dataset name: `{DATASET_NAME}`.
4. Visibility: **Private first**.
5. Create Dataset.
6. Upload all files from `hf_upload/dataset`.
7. `README.md` is the Dataset Card.
8. Verify files are visible.
9. Do not add tokens or secrets.
"""


def _final_checklist() -> str:
    return """# Hugging Face Final Checklist

- [ ] Space is private first.
- [ ] Dataset is private first.
- [ ] README renders.
- [ ] App runs.
- [ ] Sample query works.
- [ ] Source trace preview is visible.
- [ ] No verified/safe/certified claim.
- [ ] No token or secret.
- [ ] No purchase, booking, login, email, form submission, purchase, account connection, supplier verification, or contract action.
"""


def create_hf_upload_bundle() -> dict[str, Any]:
    root = _repo_root()
    try:
        from .registry_intake.real_payload_guard import detect_payload_mode
        from .registry_intake.registry_reprocess_all import run_registry_reprocess_all

        if detect_payload_mode(root / "data" / "registry" / "mcp_registry_raw_v0_1.json") in {
            "manual_raw",
            "live_raw",
        }:
            run_registry_reprocess_all()
    except Exception:
        # Packaging should still produce the best available local bundle even if
        # optional registry refresh fails in a constrained environment.
        pass

    upload_root = root / UPLOAD_ROOT
    space = upload_root / "space"
    dataset = upload_root / "dataset"

    for target in [space, dataset]:
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

    _write(space / "app.py", SPACE_APP)
    _write(space / "README.md", _space_readme())
    _copy_file(root / "hf_demo" / "requirements.txt", space / "requirements.txt")
    _copy_file(root / "hf_demo" / "sample_queries.json", space / "sample_queries.json")
    _copy_tree(root / "src" / "ai_objective_index", space / "src" / "ai_objective_index")
    _copy_tree(root / "schemas", space / "schemas")
    _copy_file(root / "reports" / "mcp_server_objective_index_v0_2.md", space / "reports" / "mcp_server_objective_index_v0_2.md")
    _copy_file(root / "reports" / "source_trace_quality_report_v0_2.md", space / "reports" / "source_trace_quality_report_v0_2.md")

    for rel in [
        "sample_index.json",
        "sample_source_traces.json",
        "golden_queries.json",
        "generated_mcp_tools_manifest.json",
    ]:
        _copy_file(root / "data" / rel, space / "data" / rel)
    for rel in [
        "mcp_registry_public_beta_mcp_dataset_v0_1.json",
        "mcp_registry_beta_candidates_v0_1.jsonl",
        "mcp_registry_source_traces_v0_1.jsonl",
    ]:
        _copy_file(root / "data" / "registry" / rel, space / "data" / "registry" / rel)
    for rel in ["final_preflight_result_v0_2.json", "realdata_claim_audit_v0_2.json"]:
        _copy_file(root / "data" / "generated" / rel, space / "data" / "generated" / rel)

    _write(dataset / "README.md", _dataset_readme())
    dataset_sources = {
        "action_objects.jsonl": root / "hf_dataset" / "action_objects.jsonl",
        "source_traces.jsonl": root / "hf_dataset" / "source_traces.jsonl",
        "objective_scores.jsonl": root / "hf_dataset" / "objective_scores.jsonl",
        "golden_queries.jsonl": root / "hf_dataset" / "golden_queries.jsonl",
        "eval_results.json": root / "hf_dataset" / "eval_results.json",
        "mcp_registry_beta_candidates.jsonl": root / "data" / "registry" / "mcp_registry_beta_candidates_v0_1.jsonl",
        "mcp_registry_source_traces.jsonl": root / "data" / "registry" / "mcp_registry_source_traces_v0_1.jsonl",
        "public_beta_mcp_dataset.json": root / "data" / "registry" / "mcp_registry_public_beta_mcp_dataset_v0_1.json",
    }
    copied_dataset_files = []
    for name, source in dataset_sources.items():
        if _copy_file(source, dataset / name):
            copied_dataset_files.append(name)

    _write(upload_root / "HF_SPACE_UPLOAD_STEPS.md", _space_steps())
    _write(upload_root / "HF_DATASET_UPLOAD_STEPS.md", _dataset_steps())
    _write(upload_root / "HF_FINAL_CHECKLIST.md", _final_checklist())

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "space_path": str(space.relative_to(root)),
        "dataset_path": str(dataset.relative_to(root)),
        "space_files": len([path for path in space.rglob("*") if path.is_file()]),
        "dataset_files": copied_dataset_files,
        "dataset_line_counts": {name: _line_count(dataset / name) for name in copied_dataset_files if name.endswith(".jsonl")},
        "read_only": True,
        "actual_upload_performed": False,
        "tokens_used": False,
        "live_network_used": False,
    }
    return result


def main() -> None:
    result = create_hf_upload_bundle()
    print(
        "hf_upload_packager: "
        f"space_files={result['space_files']} "
        f"dataset_files={len(result['dataset_files'])} "
        "actual_upload_performed=False"
    )


if __name__ == "__main__":
    main()
