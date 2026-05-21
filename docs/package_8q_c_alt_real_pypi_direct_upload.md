# Package 8Q-C-alt: Real PyPI Direct Upload Gate

Package 8Q-C-alt replaces the TestPyPI upload path because TestPyPI signup is blocked for the owner with HTTP 406. It adds a stricter real PyPI gate, an interactive twine upload runner, install verification from real PyPI, a release audit, and a post-PyPI MCP Registry gate.

It does not use TestPyPI. It does not submit to MCP Registry. It does not post to communities. It does not create or commit `.pypirc`, request tokens in chat, print tokens, pass tokens through command-line flags, force push, delete releases, or overwrite existing PyPI files.

Run the safe checks:

```powershell
python -m ai_objective_index.real_pypi_upload_gate
python -m ai_objective_index.real_pypi_upload_runner --dry-run
```

Only if the gate returns `PASS_READY_FOR_REAL_PYPI_UPLOAD`, run the upload in a local terminal:

```powershell
$env:AOI_REAL_PYPI_UPLOAD_CONFIRM="YES"
python -m ai_objective_index.real_pypi_upload_runner --execute
```

When twine prompts:

- username: `__token__`
- password: your real PyPI API token

Then verify:

```powershell
python -m ai_objective_index.real_pypi_install_verify
python -m ai_objective_index.real_pypi_release_audit
python -m ai_objective_index.mcp_registry_after_pypi_gate
```

AOI remains read-only and source-traced. The real PyPI artifact is not verified, not security certified, not a quality guarantee, not production readiness, and not purchasing advice.
