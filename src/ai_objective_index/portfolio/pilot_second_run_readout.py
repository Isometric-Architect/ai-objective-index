from __future__ import annotations

from typing import Any


def build_second_run_readout(bundle: dict[str, Any]) -> str:
    packets = bundle.get("feedback_packets", [])
    classifications = bundle.get("classifications", [])
    plans = bundle.get("second_run_plans", [])
    gates = bundle.get("second_run_gates", [])
    lines = [
        "# Pilot Feedback and Second-Run Reviewer Readout",
        "",
        "ROE-14 converts local/offline reviewer feedback into classifications, second-run plans, feedback memory updates, and second-run gates.",
        "",
        "## Feedback Summary",
        "",
        "| Vertical | Feedback category | Classification | Plan status | Gate |",
        "| --- | --- | --- | --- | --- |",
    ]
    for index, packet in enumerate(packets):
        classification = classifications[index] if index < len(classifications) else {}
        plan = plans[index] if index < len(plans) else {}
        gate = gates[index] if index < len(gates) else {}
        lines.append(
            "| "
            f"{packet.get('vertical', 'unknown')} | "
            f"{packet.get('feedback_category', 'unknown')} | "
            f"{classification.get('classification', 'UNKNOWN')} | "
            f"{plan.get('run_status', 'UNKNOWN')} | "
            f"{gate.get('decision', 'UNKNOWN')} |"
        )
    lines.extend(
        [
            "",
            "## Allowed Operations",
            "",
            "- Local receipt regeneration planning.",
            "- Local redaction checks.",
            "- Local claim-boundary checks.",
            "- Local feedback memory updates.",
            "",
            "## Forbidden Operations",
            "",
            "- GitHub API calls.",
            "- Repository cloning or URL fetching.",
            "- Issue, PR, or comment creation.",
            "- Merge, deploy, package publish, upload, or model training.",
            "- Live MCP/tool calls or external tool execution.",
            "- Credential use.",
            "",
            "## Claim Boundaries",
            "",
            "This is not external action authorization. It is not certification, legal/privacy/license/eval-clean proof, code correctness proof, product readiness, or a quality guarantee.",
            "",
            "## Known Limits",
            "",
            "- The second-run plan does not execute by default.",
            "- Feedback can request clarification, fixtures, evidence, or future local runs, but cannot authorize external actions.",
            "- Private kernel values, provider priors, thresholds, anti-gaming rules, private probes, and commercial routing policy remain non-public.",
            "",
            "## Next Actions",
            "",
            "- Collect owner-consented local artifacts if a future second-run receipt is needed.",
            "- Keep feedback redacted and local.",
            "- Run the ROE-14 gate before any ROE-15 local second-run package.",
        ]
    )
    return "\n".join(lines) + "\n"
