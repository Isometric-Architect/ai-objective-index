# AgentSec GitHub CI Bridge Limitations

The AgentSec-3 bridge is an artifact helper, not an enforcement gateway.

Current limits:

- no active workflow is created by default;
- no live MCP calls;
- no external tool execution;
- no URL fetch or crawling;
- no GitHub API calls;
- no PR comments;
- no token handling;
- no runtime sandboxing;
- no deployment, upload, registry publish, payment, booking, login, email, purchase, contract, account, supplier, or profile action.

The bridge can produce review artifacts from local manifests. It cannot certify a tool, guarantee quality, prove production readiness, or authorize external actions.

Private policy thresholds, provider priors, anti-gaming rules, private negative controls, private probe banks, and commercial routing policy remain outside the public action.
