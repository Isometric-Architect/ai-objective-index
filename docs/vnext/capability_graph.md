# Capability Graph

CapabilityGraph connects objectives, capabilities, tools, MCP servers, agents, datasets, verifiers, benchmarks, providers, failure modes, execution receipts, and risk boundaries.

Node types:

- Objective
- Capability
- Tool
- MCPServer
- Agent
- Dataset
- Verifier
- Benchmark
- Provider
- FailureMode
- ExecutionReceipt
- RiskBoundary

Edge types:

- supports
- requires
- verified_by
- fails_under
- blocked_by
- delegates_to
- substitutes_for
- composed_with
- version_of

Graph edges are evidence-carrying relationships, not absolute proof.
