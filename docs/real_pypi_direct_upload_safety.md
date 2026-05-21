# Real PyPI Direct Upload Safety

Use this path only because TestPyPI account creation is blocked.

Before upload:

1. Confirm `pyproject.toml`, `.mcp/server.json`, and `ai_objective_index.__version__` are `0.3.0a1`.
2. Confirm the wheel and sdist exist under `dist/`.
3. Run `twine check`.
4. Confirm `.pypirc` is not present in the repo.
5. Confirm the PyPI project status gate does not report a name or version conflict.

Token handling:

- Do not paste PyPI tokens into ChatGPT/Codex chat.
- Do not store tokens in files.
- Do not commit `.pypirc`.
- Do not pass token values through command-line flags.
- Let `twine` prompt interactively.
- Use username `__token__` and paste the API token only into the password prompt.

If upload fails because the version already exists, do not delete or retry blindly. Use the version conflict recovery plan and bump to `0.3.0a2` if a new build is needed.
