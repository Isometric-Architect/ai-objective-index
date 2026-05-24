# AgentSec Limitations

AgentSec-1 is not a security scanner, runtime sandbox, formal verification system, compliance tool, or external gateway.

Current limits:

- local metadata only;
- JSON manifest only;
- heuristic indicators only;
- no live MCP call;
- no external tool execution;
- no URL fetch or crawling;
- no token handling;
- no action authorization.

The scanner can add warnings, HOLD decisions, or BLOCK decisions for obvious manifest-level risks. It cannot prove a tool is complete, current, safe, secure, high quality, production ready, legally compliant, or suitable for purchase.

Private ranking weights, thresholds, anti-gaming rules, provider priors, private negative controls, private probe banks, and commercial routing policy remain non-public.
