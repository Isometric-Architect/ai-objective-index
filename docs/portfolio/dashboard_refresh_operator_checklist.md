# Dashboard Refresh Operator Checklist

1. Run `python -m ai_objective_index.portfolio.dashboard_refresh_from_feedback`.
2. Inspect `pilot_dashboard/ROE21_DASHBOARD_REFRESH_DELTA.json`.
3. Inspect `pilot_dashboard/ROE21_FEEDBACK_SECOND_RUN_STATUS_CARDS.json`.
4. Confirm AgentSec is executed and incorporated.
5. Confirm QIRA, DataCapsule, and Portfolio are skipped/HOLD, not success.
6. Inspect `pilot_dashboard/ROE21_EXTERNAL_SHARE_PACK_STALE_NOTICE.md`.
7. Run `python -m ai_objective_index.portfolio.roe21_dashboard_refresh_gate`.
8. Do not share the older external share pack as current until ROE-22 regenerates it.

Do not post, deploy, call APIs, fetch URLs, run live tools, mutate repositories, upload, train, or make certification/proof/product-readiness claims.
