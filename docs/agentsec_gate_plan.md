# AgentSec Gate Plan

AgentSec Gate is the market-facing security vertical for AI agents, MCP servers, tool manifests, APIs, file access, browser access, and code execution boundaries.

Initial MVP scope:

- scan MCP/tool metadata locally
- hash metadata and permission scopes
- flag hidden instruction and prompt-injection risk indicators
- flag namespace/lookalike risk indicators
- emit ToolRiskPacket and AgentExecutionReceipt fixtures
- return ALLOW/HOLD/BLOCK under explicit claim boundaries

AgentSec should reuse the ROE packet, residual, receipt, and action-license vocabulary. It should not start as a broad external gateway. The first version should be local metadata analysis and policy linting only.

AgentSec must not claim that a tool is verified, security certified, product ready, or authorized for external action. Later live proxy behavior should remain gated behind separate evidence and user confirmation.
