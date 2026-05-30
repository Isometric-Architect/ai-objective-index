# AOI 0.3.0a2 Version Conflict Recovery Plan

If PyPI reports that `0.3.0a2` already exists:

1. Do not retry the same distribution files blindly.
2. Do not overwrite or yank 0.3.0a1.
3. Inspect the PyPI project page manually.
4. If 0.3.0a2 is already valid and installable, run the PyPI verify helper.
5. If 0.3.0a2 is unusable, prepare a new marker-sync recovery version such as `0.3.0a3`.
6. Keep README, `.mcp/server.json`, `pyproject.toml`, and `__version__` synchronized before any new upload.

Version conflict handling does not authorize MCP Registry publish, product readiness claims, certification claims, or external actions.
