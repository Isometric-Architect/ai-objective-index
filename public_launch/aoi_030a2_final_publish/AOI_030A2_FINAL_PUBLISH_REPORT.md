# AOI 0.3.0a2 Final Publish Report

This report summarizes the guarded final distribution path for `ai-objective-index==0.3.0a2`.

| Check | Decision |
| --- | --- |
| Final preflight | `PASS_READY_FOR_FINAL_PYPI_UPLOAD` |
| Final build/twine | `PASS_FINAL_BUILD_READY` |
| PyPI upload gate | `HOLD_ENV_CONFIRM_REQUIRED` |
| PyPI upload | `HOLD_ENV_CONFIRM_REQUIRED` |
| PyPI verify | `HOLD_PYPI_UPLOAD_NOT_CONFIRMED` |
| MCP Registry gate | `HOLD_PYPI_VERIFY_REQUIRED` |
| MCP Registry publish | `HOLD_ENV_CONFIRM_REQUIRED` |
| MCP Registry reconcile | `HOLD_REGISTRY_PUBLISH_NOT_CONFIRMED` |

## Included Agent Surfaces

- Agent-native capability card.
- Discover mode for source-traced candidate discovery.
- Preflight mode for route decisions, missing fields, claim ceilings, and ResidualOps escalation.
- Read-only REST endpoints for capability-card, discover, preflight, and adoption status.
- Read-only MCP tools for capability-card, discover, preflight, explanation, and examples.
- Package-data inclusion for agent discovery artifacts, agent schemas, prompt examples, and API examples.

## Token Safety

PyPI upload uses interactive `twine upload` only after `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES`. The runner does not accept tokens as command-line arguments, does not create `.pypirc`, does not store tokens, and records only redacted status metadata.

MCP Registry publish uses `mcp-publisher` only after PyPI verification and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`. Publisher output is redacted before it is written to result files.

## Not Claimed

- No security certification.
- No legal, privacy, license, or compliance clearance.
- No code-correctness proof.
- No quality guarantee.
- No product-readiness claim.
- No action authorization.
- No private ranking weights, thresholds, provider priors, anti-gaming details, private negative controls, private probe seeds, commercial routing policy, real feedback memory, or customer data.
