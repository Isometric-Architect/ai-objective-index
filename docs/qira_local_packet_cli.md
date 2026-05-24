# QIRA Local Packet CLI

Generate and run a safe sample packet:

```powershell
python -m ai_objective_index.qira.task_cli --run-sample
```

Run a user-supplied local packet:

```powershell
python -m ai_objective_index.qira.task_cli --input path/to/qira_task_packet.json --output public_launch/qira2/QIRA2_RELEASE_GATE_REPORT.json
```

The CLI writes:

- `public_launch/qira2/QIRA2_SAMPLE_TASK_PACKET.json`
- `public_launch/qira2/QIRA2_PACKET_INTAKE_RESULT.json`
- `public_launch/qira2/QIRA2_RELEASE_GATE_REPORT.json`
- `public_launch/qira2/QIRA2_NEXT_STEPS.md`

The CLI is local/offline. It does not execute test commands, deploy code, contact a repository host, send network requests, or handle secrets.
