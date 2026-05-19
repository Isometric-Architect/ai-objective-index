# No-Contact Public Beta Strategy

AOI can run a public beta without private reviewers. Private reviewer feedback is useful, but it is not mandatory when the project has deterministic local gates, conservative launch language, and an issue-based feedback loop.

## Strategy

1. Keep the product read-only.
2. Run deterministic AI/self-review with `python -m ai_objective_index.ai_reviewer_simulation`.
3. Package GitHub Issue feedback instructions with `python -m ai_objective_index.issue_feedback_loop_packager`.
4. Guard public messages with `python -m ai_objective_index.public_beta_message_guard`.
5. Run `python -m ai_objective_index.no_contact_launch_gate`.

## What This Does Not Claim

No-contact public beta does not mean AOI is verified, security certified, quality guaranteed, production-ready, or purchasing advice. `public_beta_mcp` remains a set of source-traced Official MCP Registry metadata candidates.

## What Feedback Looks Like

Feedback should arrive as issues:

- failed query
- wrong field
- scoring dispute
- missing source trace
- docs confusion
- install failure

The owner can reproduce, classify, patch, and add valid cases to golden queries. No direct sales or personal outreach is required.
