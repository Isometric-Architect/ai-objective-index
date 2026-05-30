# Freshness And Staleness Policy

Agent outputs should include `last_checked_at`, `source_trace_age`, `registry_payload_version`, `stale_warning`, `needs_refresh`, and `refresh_next_action`.

Do not claim live freshness unless a live check was actually performed. Static sample records can support discovery, but preflight should HOLD stale or unclear metadata before external-facing recommendation.
