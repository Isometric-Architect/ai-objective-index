from __future__ import annotations

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
