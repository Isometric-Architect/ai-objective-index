# ExecutionReceipt Submission

`ExecutionReceiptSubmission` is the user- or agent-supplied record of an observed outcome.

Required fields:

- `capability_id`
- `outcome`

Important fields:

- `receipt_origin`: `self_reported`, `local_fixture`, `public_issue`, `manual_review`, `benchmark`, or `unknown`
- `outcome`: `success`, `partial`, `fail`, `hold`, or `blocked`
- `error_type`: `install_failure`, `docs_missing`, `policy_unclear`, `source_trace_missing`, `wrong_ranking`, `stale_metadata`, `api_failure`, `security_concern`, `unsupported_claim`, or `unknown`
- `must_not_claim`: default claim boundaries

Validation blocks forbidden external-action claims and unsupported verification/certification/quality claims. Self-reported success can add notes, but it cannot verify the capability.

