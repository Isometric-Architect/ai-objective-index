from __future__ import annotations

from typing import Any


def build_feedback_reply_readout(bundle: dict[str, Any]) -> str:
    packets = bundle.get("packets", [])
    classifications = bundle.get("classifications", [])
    routes = bundle.get("routes", [])
    triage = bundle.get("triage", [])
    memory = bundle.get("memory_candidates", [])
    second_run = bundle.get("second_run_candidates", [])
    rows = []
    for index, packet in enumerate(packets):
        classification = classifications[index] if index < len(classifications) else {}
        route = routes[index] if index < len(routes) else {}
        triage_entry = triage[index] if index < len(triage) else {}
        rows.append(
            "| "
            + " | ".join(
                [
                    packet.get("reply_id", ""),
                    packet.get("related_vertical", ""),
                    classification.get("classification", ""),
                    route.get("selected_vertical", ""),
                    triage_entry.get("status", ""),
                ]
            )
            + " |"
        )
    table = "\n".join(rows)
    return f"""# Feedback Reply Intake Readout

This readout summarizes local/offline feedback replies. It does not send replies, create GitHub issues, post comments, call APIs, fetch URLs, mutate repositories, upload data, train models, or authorize external action.

## What Was Ingested

- Reply packets: `{len(packets)}`
- Classifications: `{len(classifications)}`
- Routes: `{len(routes)}`
- Triage entries: `{len(triage)}`
- Memory candidates: `{len(memory)}`
- Second-run candidates: `{len(second_run)}`

## Route And Triage

| Reply | Related vertical | Classification | Route | Status |
| --- | --- | --- | --- | --- |
{table}

## Redaction

Redaction decision: `{bundle.get("redaction", {}).get("decision", "UNKNOWN")}`.

## Claim Boundaries

- Not reply sending.
- Not GitHub issue creation.
- Not security certification.
- Not code correctness proof.
- Not legal, privacy, license, or eval-clean proof.
- Not product readiness or quality guarantee.
- No external action authorization.

## Known Limits

Feedback replies can become local memory or second-run candidates. They cannot authorize posting, issue creation, repo mutation, certification, proof, readiness claims, or live actions.

## Next Actions

Inspect blocked or held replies manually. For accepted second-run candidates, proceed only with redacted local artifacts and the existing local second-run gate.
"""
