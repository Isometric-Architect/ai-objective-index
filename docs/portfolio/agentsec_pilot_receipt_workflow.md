# AgentSec Pilot Receipt Workflow

The intended workflow is:

1. Supply a local MCP/tool manifest or use the public-safe sample fixture.
2. Run AgentSec local metadata checks.
3. Package the result into an AgentSec pilot receipt.
4. Generate a reviewer readout.
5. Generate a feedback memory entry.
6. Use the feedback entry to decide future public-safe fixture or policy-profile updates.

No step requires live MCP calls, external tool execution, GitHub API calls, PR comments, tokens, or external repository modification.
