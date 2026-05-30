# External Share V2 Operator Checklist

1. Run `python -m ai_objective_index.portfolio.external_share_refresh_builder`.
2. Open `external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.html` locally.
3. Confirm the claim ceiling banner is visible.
4. Confirm AgentSec is shown as executed/incorporated.
5. Confirm QIRA, DataCapsule, and Portfolio are shown as `skipped_missing_artifact`.
6. Confirm skipped candidates are explained as HOLD, not success.
7. Confirm `external_action_count = 0`.
8. Run `python -m ai_objective_index.portfolio.roe22_external_share_refresh_gate`.
9. Run `python -m ai_objective_index.portfolio.external_share_refresh_archive --dry-run` if an archive check is needed.

Do not deploy, post, fetch, call APIs, use live connectors, upload data, train models, mutate repositories, use credentials, expose private kernels, or make certification/proof/product-readiness/action-authorization claims.
