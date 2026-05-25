# AgentSec-8 Operator Runbook

AgentSec-8 provides an opt-in workflow artifact template. It is not active in this repository by default.

## How To Use

1. Review `examples/agentsec8_optional_pr_review_artifact_workflow.yml`.
2. Copy it into `.github/workflows/` only in a repository where the owner wants the workflow enabled.
3. Provide a committed MCP/tool manifest set path when manually dispatching the workflow.
4. Download the generated JSON/Markdown artifact and review HOLD/BLOCK items before use.

## Boundaries

- The template uses `workflow_dispatch`, not automatic PR posting.
- The template uploads local review artifacts; it does not post comments.
- AgentSec does not call live MCP servers, execute tools, fetch URLs, call GitHub APIs, handle tokens, certify security, guarantee quality, prove product readiness, or authorize external actions.
- Keep private thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, and commercial policy outside public artifacts.
