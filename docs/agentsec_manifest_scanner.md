# AgentSec Manifest Scanner

The AgentSec manifest scanner is intentionally narrow in AgentSec-1.

It does:

- parse a local JSON MCP/tool manifest;
- hash the manifest metadata;
- scan local text fields for risky instruction, permission, namespace, action, and claim indicators;
- emit a `ToolRiskPacket`, `AgentSecScanResult`, and `AgentSecActionBoundaryReceipt`.

It does not:

- call a live MCP server;
- execute tools;
- run shell commands from the manifest;
- fetch URLs;
- open browsers;
- log in;
- send email;
- perform payment, booking, purchase, contract, account, supplier, or profile actions;
- certify safety, security, quality, or readiness.

AgentSec-1 is a pre-use metadata lint layer. Later proxy or live gate behavior must remain separately gated.
