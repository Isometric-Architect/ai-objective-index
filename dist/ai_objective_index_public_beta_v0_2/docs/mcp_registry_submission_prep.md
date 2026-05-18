# MCP Registry Submission Prep

Package 7A prepares AOI for manual MCP registry review. It does not submit automatically.

Package 7B can include this checklist in a local public beta release candidate pack. Submission remains manual.

## Manual Checklist

- README is complete and current.
- `data/generated_mcp_tools_manifest.json` is generated.
- Tool manifest includes read-only `search`, `fetch`, and AOI-specific tools.
- Read-only safety statement is visible.
- Forbidden actions are listed and not exposed as tools.
- `python -m ai_objective_index.mcp_smoke` passes.
- Source trace examples exist.
- Limitations are explicit.
- `sample`, `generated`, and `integrated` data scopes are documented.
- Generated data remains `EXTRACTED_UNVERIFIED`.

Do not claim official listing, registry acceptance, certification, or ecosystem endorsement until a human submits AOI and the registry accepts it.

## v0.2 Real-Data Candidate Note

Package 8A may prepare a release pack with `public_beta_mcp` candidates from Official MCP Registry metadata. That does not mean AOI has submitted to, been accepted by, or been endorsed by any registry. Registry submission remains manual.

## Not Submitted By This Repo

This repository does not automatically publish, post, submit, authenticate, or connect accounts for registry submission.

Package 8B adds `launch/manual_public_beta_v0_2/MCP_REGISTRY_SUBMISSION_DRAFT.md`. It is a draft only and does not submit anything.
