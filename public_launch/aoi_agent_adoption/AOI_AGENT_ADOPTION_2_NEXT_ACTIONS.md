# AOI Agent Adoption 2 Next Actions

Recommended next package: AOI 0.3.0a2 final PyPI upload + MCP Registry publish.

Before upload, rerun tests, marker sync, build/twine check, package-data audit, and MCP publisher validate. Upload must remain an explicit local action with interactive token entry and `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES`. MCP Registry publish must remain an explicit local action after PyPI verification and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.
