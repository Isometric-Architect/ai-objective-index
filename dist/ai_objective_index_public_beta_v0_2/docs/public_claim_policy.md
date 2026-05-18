# Public Claim Policy

AOI public claims must distinguish implemented product behavior from research ambition.

## Allowed Public Claims

- AOI is a read-only MCP/API benchmark tool.
- AOI is an objective ranking and comparison engine for AI tools, APIs, SaaS products, and MCP servers.
- AOI surfaces source traces, missing fields, score components, warnings, and decision receipts.
- AOI supports sample, generated, integrated, curated, public_beta, mcp_registry, and public_beta_mcp local data scopes.
- AOI can describe public_beta_mcp as source-traced Official MCP Registry metadata candidates.
- AOI is experimental v0.1/v0.2 software.
- AOI can be used for benchmark-style testing and failure-loop feedback.

## Forbidden Public Claims

- All AI will use AOI.
- AOI is an official standard.
- ActionRank, ObjectiveRank, or ObjectiveScore guarantees quality.
- AOI provides legal, security, compliance, procurement, purchasing, financial, medical, or professional certification.
- AOI is purchasing advice.
- AOI automatically executes payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract signing.
- AOI verifies MCP servers or certifies MCP server security.

## Productization Clarification

Internal research claim ceilings limit public claims. They do not ban product development, algorithms, GitHub repos, MCP/API prototypes, benchmark demos, or commercialization experiments.

When public copy is uncertain, use the safer formulation: AOI is experimental read-only software with source-traced benchmark outputs, not a guarantee or execution authority.

## Release Candidate Review

Before manual public beta publishing, run:

```powershell
python -m ai_objective_index.release_claim_audit
python -m ai_objective_index.realdata_claim_audit
python -m ai_objective_index.launch_claim_guard
```

Risky phrases inside forbidden-claim sections are allowed as negative examples. Risky phrases used as positive claims should be rewritten.
