# ROE-5 Dry-Run Onboarding Plan

Recommended first pilot: `AgentSec Gate` (`AgentSec-8`)

Reason: best first external security-facing pilot if repository has MCP/tool manifests

## Dry Run Steps

1. Review `examples/agentsec8_optional_pr_review_artifact_workflow.yml`.
2. Confirm repository owner consent before copying any workflow.
3. Prepare the required input: committed MCP/tool manifest JSON or manifest set.
4. Keep the first run manual.
5. Download the workflow artifact.
6. Record HOLD/BLOCK findings and decide whether a second run is useful.

## Boundaries

This plan does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/evaluation status, provide purchasing advice, or authorize actions.
