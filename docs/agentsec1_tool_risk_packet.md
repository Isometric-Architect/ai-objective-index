# AgentSec-1 Tool Risk Packet

AgentSec-1 adds a local-only metadata scanner for MCP/tool manifests. It reads a repository-supplied JSON manifest, hashes the metadata, extracts permission indicators, and emits a conservative `ToolRiskPacket`.

The packet can record:

- permission scope indicators for network, file, write, secret, browser, and code-execution access;
- hidden-instruction and prompt-injection indicators in local metadata;
- namespace or ownership review signals;
- forbidden real-world action language;
- unsupported verification, safety, certification, quality, or product-readiness claims;
- ALLOW/HOLD/BLOCK-style route boundaries.

`ALLOW_METADATA_ONLY` only means the local metadata scan did not find blocking indicators in the supplied fixture. It is not verification, safety, security certification, quality guarantee, production readiness, or action authorization.

Run the sample:

```powershell
python -m ai_objective_index.agentsec.cli_demo --run-sample
```

Outputs are written under `public_launch/agentsec1/`.
