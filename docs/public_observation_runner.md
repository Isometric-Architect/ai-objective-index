# Public Observation Runner

The observation runner records public beta health without launching any announcement.

Phases:

- `0h`: create the first metrics snapshot and active observation log.
- `24h`: write/update a 24-hour template.
- `48h`: write/update a 48-hour template.
- `72h`: write/update a 72-hour template.

Commands:

```powershell
python -m ai_objective_index.public_observation_runner --phase 0h
python -m ai_objective_index.public_observation_runner --phase 24h
python -m ai_objective_index.public_observation_runner --phase 48h
python -m ai_objective_index.public_observation_runner --phase 72h
```

If GitHub or Hugging Face status checks are unavailable, the snapshot records `not_checked`; that is not a failure. Use the log to capture GitHub stars, open issues, HF Space status, HF Dataset visibility, failed queries, and source-trace reports.

Do not treat quiet early metrics as failure. No immediate attention does not mean the public beta failed.
