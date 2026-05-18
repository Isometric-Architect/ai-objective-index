# No-Secrets Policy

Package 8B scans launch-facing text files for likely secrets.

## Scanned Areas

- `README.md`
- `docs/`
- `examples/`
- `hf_demo/`
- `hf_dataset/`
- `release/public_beta_v0_2/`
- `launch/manual_public_beta_v0_2/`

Large generated raw registry JSON is not scanned by default.

## Blocked Patterns

- `sk-`
- `ghp_`
- `hf_`
- `xoxb-`
- `api_key=`
- `password=`
- bearer token strings
- `PRIVATE KEY` example pattern, not a real secret
- `AWS_ACCESS_KEY_ID` example pattern, not a real secret
- `AWS_SECRET_ACCESS_KEY` example pattern, not a real secret

Clearly redacted placeholders may be warnings instead of blocks. Real-looking tokens must be removed before manual launch.
