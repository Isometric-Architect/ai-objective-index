# Second-Run Feedback Memory

ROE-15 updates feedback memory from ROE-14.

Entries can move from `pending` to:

- `incorporated`: feedback was reflected in explanation, fixture candidate, or next-action updates;
- `pending_with_followup`: feedback created a local evidence request that still needs owner-provided material;
- `rejected`: feedback was blocked because it requested external action, included private data, or asked for certification/proof/readiness wording.

Feedback memory remains a local planning artifact. It does not create issues, comments, PRs, branches, merges, deployments, uploads, or registry submissions.
