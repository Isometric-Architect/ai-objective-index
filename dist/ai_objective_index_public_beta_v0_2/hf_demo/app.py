from __future__ import annotations

import json
from pathlib import Path
from typing import Any


try:
    import gradio as gr
except Exception:  # pragma: no cover - environment-dependent optional dependency.
    gr = None


def _ensure_src_import() -> None:
    import sys

    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


_ensure_src_import()

from ai_objective_index.mcp_tools import get_source_trace, search_objectives  # noqa: E402


def _safe_data_scope(data_scope: str | None) -> str:
    value = (data_scope or "sample").strip().lower()
    if value not in {
        "sample",
        "generated",
        "integrated",
        "curated",
        "public_beta",
        "mcp_registry",
        "public_beta_mcp",
    }:
        return "sample"
    return value


def run_demo_query(
    query: str,
    objective: str = "",
    limit: int = 5,
    data_scope: str = "sample",
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """Run a local read-only AOI demo query.

    Returns a Markdown summary, table-compatible rows, and raw JSON payload.
    """

    safe_query = (query or "").strip() or "cheap image generation API with commercial use terms"
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
                "status": item.get("status"),
                "missing_fields": ", ".join(item.get("missing_fields", [])[:4]),
            }
        )
    if rows:
        source_trace_preview = get_source_trace(rows[0]["object_id"], data_scope=scope)

    top = rows[0] if rows else {}
    summary = "\n".join(
        [
            "## AI Objective Index Demo Result",
            "",
            "Read-only local data. Not a quality guarantee or purchasing advice.",
            "",
            f"Query: `{safe_query}`",
            f"Data scope: `{scope}`",
            f"Top result: `{top.get('name', 'none')}`",
            f"Objective score: `{top.get('score', 'n/a')}`",
            "Registry metadata candidate, not verified." if scope == "public_beta_mcp" and rows else "",
            f"Warnings: `{'; '.join(result.get('warnings', [])) or 'none'}`",
        ]
    )
    payload = {
        "read_only": True,
        "data_scope": scope,
        "query_result": result,
        "source_trace_preview": source_trace_preview,
    }
    return summary, rows, payload


def build_demo():
    if gr is None:
        return None

    with gr.Blocks(title="AI Objective Index") as demo:
        gr.Markdown(
            "# AI Objective Index\nRead-only objective-fit ranking for AI tools/APIs/SaaS/MCP sample records."
        )
        query = gr.Textbox(
            label="Query",
            value="cheap image generation API with commercial use terms",
        )
        objective = gr.Textbox(label="Objective", value="low cost commercial use")
        limit = gr.Slider(label="Limit", minimum=1, maximum=10, step=1, value=5)
        data_scope = gr.Dropdown(
            label="Data scope",
            choices=[
                "sample",
                "generated",
                "integrated",
                "curated",
                "public_beta",
                "mcp_registry",
                "public_beta_mcp",
            ],
            value="sample",
        )
        run = gr.Button("Run read-only query")
        summary = gr.Markdown()
        table = gr.Dataframe(label="Results", interactive=False)
        output = gr.JSON(label="JSON output")
        run.click(
            run_demo_query,
            inputs=[query, objective, limit, data_scope],
            outputs=[summary, table, output],
        )
    return demo


def main() -> None:
    if gr is None:
        print("Install gradio to run the Hugging Face demo locally.")
        sample_summary, sample_rows, sample_payload = run_demo_query(
            "cheap image generation API with commercial use terms"
        )
        print(sample_summary)
        print(json.dumps({"rows": sample_rows[:2], "read_only": sample_payload["read_only"]}, indent=2))
        return
    build_demo().launch()


if __name__ == "__main__":
    main()
