# AOI 0.3.0a2 MCP Registry Recovery

AOI 0.3.0a2 exists to recover from the MCP Registry metadata mismatch seen after the real PyPI 0.3.0a1 upload. The recovery publishes a new PyPI artifact with synchronized README and `.mcp/server.json` metadata instead of overwriting or yanking 0.3.0a1.

Canonical metadata:

- server name: `io.github.Isometric-Architect/ai-objective-index`
- package: `ai-objective-index`
- version: `0.3.0a2`
- registry type: `pypi`
- README marker: `mcp-name: io.github.Isometric-Architect/ai-objective-index`

Recovery flow:

1. Run marker sync audit.
2. Build wheel/sdist.
3. Run `twine check`.
4. Gate real PyPI upload.
5. Upload only with `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES` and twine's interactive token prompt.
6. Verify install from real PyPI.
7. Validate `.mcp/server.json` with local `mcp-publisher`.
8. Publish to MCP Registry only with `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.
9. Reconcile registry search results.

This is a metadata recovery path. It is not security certification, code correctness proof, legal/privacy/license/evaluation proof, product readiness, quality guarantee, or external action authorization.
