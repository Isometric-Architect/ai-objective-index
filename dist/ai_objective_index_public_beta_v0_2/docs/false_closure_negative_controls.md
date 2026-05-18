# False-Closure Negative Controls

Package 6D-S adds false-closure controls under `data/negative_controls/`.

Controls include:

- missing pricing must not produce `price_clear`;
- missing commercial terms must not produce `commercial_use_allowed`;
- source URL presence alone must not become a source-supported field;
- generated data must not become `VERIFIED`;
- read permission must not become train/share/action permission;
- stale data must not become current truth;
- sample data must not be presented as live crawl data;
- objective score must not become a quality guarantee;
- read-only MCP output must not expose write/action tools;
- every HOLD must include `next_action`.

Run:

```powershell
python -m ai_objective_index.negative_control_runner
```

PASS condition:

- `false_BOX = 0`
- `forbidden_promotions = 0`
- blocked actions are blocked
- every HOLD has a next action
