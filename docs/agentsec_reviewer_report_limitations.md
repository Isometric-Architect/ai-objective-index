# AgentSec Reviewer Report Limitations

AgentSec reviewer reports are local artifact summaries. They help a maintainer inspect MCP or tool manifest metadata, but they are not independent verification.

## What The Report Can Say

- which local manifests were reviewed
- which local policy profile was applied
- which candidates were `ALLOW_METADATA_ONLY`, `HOLD_REVIEW_REQUIRED`, or `BLOCK_POLICY_RISK`
- which missing or risky metadata patterns need review
- which public artifacts were generated

## What The Report Must Not Say

- Do not say that a tool is verified.
- Do not say that a tool is safe.
- Do not say that a tool is security certified.
- Do not say that quality is guaranteed.
- Do not say that a tool is production ready.
- Do not say that external actions are authorized.
- Do not say that live gateway protection was provided.

## Operational Boundary

The report is a draft review artifact. Posting it to a pull request, enabling a workflow, calling live MCP servers, executing tools, changing repository state, or authorizing use requires a separate explicit owner action.
