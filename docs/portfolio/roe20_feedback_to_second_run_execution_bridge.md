# ROE-20 Feedback-To-Second-Run Execution Bridge

ROE-20 connects local feedback reply second-run candidates from ROE-19 to the conservative local second-run pattern from ROE-15.

It executes only candidates marked `READY_FOR_LOCAL_SECOND_RUN`. Candidates on HOLD remain skipped and receive a skipped-candidate report with the missing artifact, consent, or context needed before retry.

ROE-20 is local/offline only. It does not call GitHub APIs, create issues or comments, fetch URLs, clone repositories, run live MCP/tool calls, mutate repositories, post externally, merge, deploy, publish packages, upload data, train models, use credentials, or request tokens.

The bridge is not an external pilot, security certification, code correctness proof, legal/privacy/license/eval-clean proof, product readiness, quality guarantee, or external action authorization.
