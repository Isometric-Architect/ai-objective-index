# TestPyPI Upload Safety

Package 8Q-A resumed stops before upload. The next upload package should use TestPyPI first and should not touch real PyPI until the TestPyPI install path passes.

Safety rules:

- Do not paste PyPI/TestPyPI tokens into ChatGPT/Codex chat.
- Do not commit `.pypirc`.
- Do not store token files in the repository.
- Do not upload real PyPI until TestPyPI install verification passes.
- Do not submit MCP Registry metadata until the PyPI package exists and registry readiness passes.
# TestPyPI Blocked Fallback

The owner reported TestPyPI signup is blocked with HTTP 406. Package 8Q-C-alt therefore skips TestPyPI and uses a stricter real PyPI direct upload gate.

This fallback does not weaken token safety:

- do not paste tokens into ChatGPT/Codex chat;
- do not create or commit `.pypirc`;
- do not pass tokens through command-line flags;
- use twine's local interactive prompt only;
- upload only after `python -m ai_objective_index.real_pypi_upload_gate` returns `PASS_READY_FOR_REAL_PYPI_UPLOAD`.

If a later TestPyPI path becomes available, it can be used again before a future stable release.
