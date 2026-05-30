from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_discovery_personas import OUTREACH_DIR, timestamp


LINK_PACK_PATH = OUTREACH_DIR / "PILOT_LINK_PACK.md"
LINK_PACK_JSON_PATH = OUTREACH_DIR / "PILOT_LINK_PACK.json"


KNOWN_LINKS = {
    "github_repo": "https://github.com/Isometric-Architect/ai-objective-index",
    "pypi_package": "https://pypi.org/project/ai-objective-index/0.3.0a1/",
    "hugging_face_space": "https://huggingface.co/spaces/edict-lab/ai-objective-index-demo",
    "hugging_face_dataset": "https://huggingface.co/datasets/edict-lab/ai-objective-index-sample",
    "external_share_pack_local_path": "external_share_pack/README_EXTERNAL_SAFE_DEMO.md",
    "dashboard_local_path": "pilot_dashboard/RESIDUALOPS_PILOT_DASHBOARD.html",
    "portfolio_readout_local_path": "pilot_receipts/portfolio/RESIDUALOPS_PORTFOLIO_REVIEWER_READOUT.md",
    "feedback_form_template_path": "pilot_outreach/PILOT_FEEDBACK_INTAKE_FORM_TEMPLATE.md",
    "mcp_registry_entry": "TODO: MCP Registry submission is not completed.",
}


def build_link_pack_markdown() -> str:
    lines = [
        "# Pilot Link Pack",
        "",
        "Use these links or local paths only after manual review. Replace TODO entries before any external message.",
        "",
    ]
    for key, value in KNOWN_LINKS.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "Do not include tokens, credentials, raw private data, private kernels, or live connector secrets in any message.",
            "This link pack does not send messages, post anywhere, call APIs, or authorize external action.",
            "",
        ]
    )
    return "\n".join(lines)


def build_link_pack_payload() -> dict[str, Any]:
    return {
        "schema": "ResidualOps_PilotLinkPack/v0.1",
        "generated_at": timestamp(),
        "links": KNOWN_LINKS,
        "uses_todo_for_unknown": True,
        "auto_post_performed": False,
        "external_api_used": False,
    }


def write_link_pack() -> dict[str, Any]:
    root = _repo_root()
    payload = build_link_pack_payload()
    (root / LINK_PACK_PATH).parent.mkdir(parents=True, exist_ok=True)
    (root / LINK_PACK_PATH).write_text(build_link_pack_markdown(), encoding="utf-8")
    (root / LINK_PACK_JSON_PATH).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload
