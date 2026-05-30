# AOI Public Discovery Smoke

AOI Agent Discovery 3 checks whether `ai-objective-index==0.3.0a2` can be installed from public PyPI and discovered through the MCP Registry after the final publish.

The smoke checks are intentionally narrow:

- install the public PyPI package in a temporary environment;
- verify the installed version and agent-adoption package data;
- run local discover/preflight samples from the installed package;
- query MCP Registry discovery for the canonical server name when network access is available;
- record PASS or a propagation HOLD without republishing.

This is a distribution smoke. It is not security certification, product readiness, legal/privacy/license clearance, or action authorization.
