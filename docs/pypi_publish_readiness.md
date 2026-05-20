# PyPI Publish Readiness

The PyPI readiness helper checks local package metadata, builds local distribution files when the `build` module is available, and runs `twine check` when `twine` is available.

It does not upload anything.

Token safety:

- Do not paste PyPI tokens into chat.
- Do not save tokens in the repository.
- Do not commit tokens.
- Use a scoped PyPI or TestPyPI token only during manual upload.

Expected commands:

```powershell
python -m ai_objective_index.package_metadata_audit
python -m ai_objective_index.pypi_publish_readiness
python -m ai_objective_index.pypi_upload_instructions
```

Package 8Q-A adds the local build path:

```powershell
python -m ai_objective_index.local_build_tools --check
python -m ai_objective_index.local_build_tools --install
python -m ai_objective_index.dist_build_runner
python -m ai_objective_index.local_install_smoke
python -m ai_objective_index.pypi_readiness_refresh
```

These commands build and inspect local artifacts only. They do not upload to TestPyPI or PyPI.

Package 9A pauses PyPI upload while AOI vNext positioning is aligned around the AI Agent Capability Trust Router strategy. Local build artifacts can remain available, but upload is still HOLD.
