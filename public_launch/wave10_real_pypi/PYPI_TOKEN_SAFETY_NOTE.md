# PyPI Token Safety Note

- Do not paste token into ChatGPT/Codex chat.
- Do not commit `.pypirc`.
- Twine username should be `__token__`.
- Twine password should be the real PyPI API token value, including the `pypi-` prefix.
- Enter the token only into the local terminal prompt from `twine`.
- If a token is exposed, revoke it immediately in PyPI account settings.
- After a successful upload, revoke the token if no more uploads are needed.
- First upload may require an account-scoped token because a project-scoped token cannot exist before the project exists.

Package 8Q-C-alt never stores, prints, requests in chat, or commits PyPI tokens.
