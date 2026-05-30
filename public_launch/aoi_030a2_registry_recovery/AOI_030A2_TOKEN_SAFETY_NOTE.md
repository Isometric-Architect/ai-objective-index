# AOI 0.3.0a2 Token Safety Note

The recovery helpers do not request tokens in chat, do not pass tokens on command-line flags, and do not write `.pypirc`.

For PyPI upload, use twine's local interactive prompt only:

```powershell
python -m twine upload dist/ai_objective_index-0.3.0a2-py3-none-any.whl dist/ai_objective_index-0.3.0a2.tar.gz
```

Username should be `__token__`. The API token should be entered only into the local prompt.

For MCP Registry publish, use local `mcp-publisher` login. Do not paste GitHub tokens into files, command-line flags, docs, issues, pull requests, or chat.
