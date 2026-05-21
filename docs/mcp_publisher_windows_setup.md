# MCP Publisher Windows Setup

Beginner-safe path:

1. Open the official `modelcontextprotocol/registry` GitHub releases page.
2. Download `mcp-publisher_windows_amd64.tar.gz`.
3. Extract only `mcp-publisher.exe`.
4. Place it under `tools/mcp-publisher/` or another local folder.
5. Run `python -m ai_objective_index.mcp_publisher_installer --check`.
6. Run `python -m ai_objective_index.mcp_publisher_auth_check --login`.

Do not paste GitHub tokens into chat. Use the browser/device auth flow shown by `mcp-publisher`. Do not commit downloaded credentials or token files.

The local `tools/mcp-publisher/` folder is ignored so the binary is not accidentally committed.
