# Feedback Second-Run Operator Checklist

1. Run `python -m ai_objective_index.portfolio.feedback_second_run_executor --sample`.
2. Inspect the selection report.
3. Confirm only READY candidates executed.
4. Inspect skipped-candidate reports for HOLD/BLOCK items.
5. Inspect the redaction report.
6. Run `python -m ai_objective_index.portfolio.roe20_feedback_second_run_bridge_gate`.
7. Do not post, create issues, comment, call APIs, fetch URLs, clone, merge, deploy, publish, upload, train, use live MCP/tools, or use credentials.
8. Do not present the output as certification, proof, product readiness, quality guarantee, or action authorization.
