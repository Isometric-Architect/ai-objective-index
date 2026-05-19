# AI Reviewer Simulation

`python -m ai_objective_index.ai_reviewer_simulation` runs deterministic local checks that simulate five reviewer perspectives without calling an external LLM.

## Reviewer Roles

- `skeptic_reviewer`: checks public claims and verifies `public_beta_mcp` is not described as verified.
- `developer_reviewer`: checks README, setup/demo commands, and smoke documentation.
- `agent_user_reviewer`: checks MCP manifest, OpenAPI, Hugging Face links, and source-trace visibility.
- `data_quality_reviewer`: checks public beta candidate count, source traces, fixture leakage, and raw payload mode.
- `business_positioning_reviewer`: checks positioning, target users, and overclaim risk.

## Output

The command writes `public_launch/AI_REVIEWER_SIMULATION_RESULT.json`.

Each reviewer emits:

- `PASS`, `HOLD`, or `BLOCK`
- findings
- required fixes
- confidence
- evidence files checked

This is a launch discipline check, not a product-readiness guarantee.
