# QIRA PR Diff Packet Limitations

QIRA's PR packet generator intentionally accepts only local metadata supplied by the repository owner or CI job:

- unified diff text from a local file;
- comma-separated changed-file paths;
- task and patch summary text;
- recorded test/static-check command strings;
- externally supplied test result summaries.

It does not fetch pull requests, follow links, call GitHub APIs, run `git`, execute project commands, apply patches, or inspect live services.

## Conservative Defaults

If changed files are missing, QIRA-5 returns `HOLD_NO_CHANGED_FILES`.

If paths touch dependency, config, CI, generated/data, or unknown surfaces, QIRA-5 may generate the packet but keep a hold reason for reviewer attention.

If paths reference secret, private, credential, `.env`, `.pypirc`, absolute, or repository-escape patterns, QIRA-5 blocks the packet path surface.

## Evidence Boundary

QIRA-5 can record test commands and test summaries supplied by another system. It cannot turn those records into code verification, security certification, quality guarantee, legal compliance, production readiness, deployment approval, or external action authorization.
