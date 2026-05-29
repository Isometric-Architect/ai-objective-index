from __future__ import annotations

import html
from typing import Any


def _rows(items: list[dict[str, Any]], columns: list[str]) -> str:
    body = []
    for item in items:
        body.append("<tr>" + "".join(f"<td>{html.escape(str(item.get(column, '')))}</td>" for column in columns) + "</tr>")
    return "\n".join(body)


def build_dashboard_html(dashboard: dict[str, Any]) -> str:
    cards = _rows(
        dashboard["vertical_status_cards"],
        ["display_name", "primary_decision", "allow_count", "hold_count", "block_count", "latest_gate_status", "feedback_status"],
    )
    gates = _rows(
        [{"gate": key, "decision": value} for key, value in dashboard["gate_status"].items()],
        ["gate", "decision"],
    )
    feedback_rows = _rows(
        dashboard["feedback_memory_summary"].get("entries", []),
        ["vertical", "new_status", "follow_up_actions"],
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ResidualOps Pilot Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #1f2933; background: #fafafa; }}
    .banner {{ border: 2px solid #334e68; background: #eef4f8; padding: 12px; margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0; background: white; }}
    th, td {{ border: 1px solid #ccd6dd; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f0f4f8; }}
    code {{ background: #edf2f7; padding: 2px 4px; }}
  </style>
</head>
<body>
  <div class="banner">
    <strong>Local/static artifact only.</strong>
    This dashboard summarizes local receipts and gates. It is not certification, proof, product readiness, or external action authorization.
  </div>
  <h1>ResidualOps Pilot Dashboard</h1>
  <p>Dashboard ID: <code>{html.escape(dashboard["dashboard_id"])}</code></p>
  <h2>Verticals</h2>
  <table>
    <thead><tr><th>Vertical</th><th>Decision</th><th>ALLOW</th><th>HOLD</th><th>BLOCK</th><th>Gate</th><th>Feedback</th></tr></thead>
    <tbody>{cards}</tbody>
  </table>
  <h2>Gates</h2>
  <table>
    <thead><tr><th>Gate</th><th>Decision</th></tr></thead>
    <tbody>{gates}</tbody>
  </table>
  <h2>Feedback Memory</h2>
  <table>
    <thead><tr><th>Vertical</th><th>Status</th><th>Follow-up</th></tr></thead>
    <tbody>{feedback_rows}</tbody>
  </table>
  <h2>Claim Boundaries</h2>
  <ul>
    <li>Not an external pilot.</li>
    <li>Not security certification.</li>
    <li>Not code correctness proof.</li>
    <li>Not legal, privacy, license, or eval-clean proof.</li>
    <li>Not a quality guarantee.</li>
    <li>Not product readiness.</li>
    <li>No external action authorization.</li>
  </ul>
</body>
</html>
"""
