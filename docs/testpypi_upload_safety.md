# TestPyPI Upload Safety

Package 8Q-A resumed stops before upload. The next upload package should use TestPyPI first and should not touch real PyPI until the TestPyPI install path passes.

Safety rules:

- Do not paste PyPI/TestPyPI tokens into ChatGPT/Codex chat.
- Do not commit `.pypirc`.
- Do not store token files in the repository.
- Do not upload real PyPI until TestPyPI install verification passes.
- Do not submit MCP Registry metadata until the PyPI package exists and registry readiness passes.
