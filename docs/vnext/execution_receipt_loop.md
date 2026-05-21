# ExecutionReceipt Loop

The ExecutionReceipt loop connects route decisions to local memory.

```text
objective route -> manual use outcome -> receipt validation -> local receipt store -> receipt memory -> route overlay
```

AOI stores only the reported outcome and conservative metadata. It does not run the capability, open links, execute a probe, or contact external services.

Package 9E adds a separate local probe-before-use loop. Receipts remain manual/local outcome memory; probe receipts remain deterministic local metadata checks. Neither one is independent verification or action authorization.

Receipts can:

- record known failures;
- record missing fields found during use;
- add residual notes;
- add warnings to a route;
- downgrade a candidate when failure signals are present.

Receipts cannot:

- turn HOLD into verified;
- certify security;
- guarantee quality;
- authorize external actions;
- replace current source-trace review.
