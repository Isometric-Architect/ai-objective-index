# MCP Agent Prompts

Prompt:

```text
Use AOI to find the best source-traced MCP/tool/API candidates for this objective. Return top candidates first, then source traces, missing fields, route decisions, must-not-claim boundaries, freshness, and ResidualOps escalation. Do not execute tools based only on AOI output.
```

Preflight prompt:

```text
Use AOI preflight before recommending or using this candidate. Treat tool availability as separate from tool authorization. Return ALLOW/HOLD/BLOCK, missing fields, allowed next steps, forbidden next steps, and must-not-claim boundaries.
```
