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

Package 9B keeps the pause in place while the Capability Trust Schema MVP is introduced. Local build artifacts remain useful for future packaging, but TestPyPI/PyPI upload should not resume until the vNext route-decision language and public claim boundaries stay stable.

Package 9C keeps the pause in place while Objective Router REST/MCP surfaces are introduced. Packaging can resume later only after these surfaces preserve read-only behavior and conservative claim boundaries.

Package 9F adds a distribution gate before 8Q-A resumes. It recommends choosing `0.3.0` or `0.3.0a1` for the vNext package surface before any upload-oriented package. 9F does not upload; it only prepares the local build path to resume safely.

Package 8Q-A resumed uses `0.3.0a1` as the first vNext build candidate. It builds local wheel/sdist artifacts and runs `twine check`, but still does not upload to TestPyPI or PyPI.

Package 8Q-C-alt handles the TestPyPI signup failure by adding a strict real PyPI direct upload gate. It checks the `0.3.0a1` build, PyPI project/version status, `.pypirc` absence, token safety, and twine metadata before allowing an interactive twine upload. Tokens must be entered only into the local twine prompt and never into chat, files, or command-line flags.

After a real PyPI upload, run:

```powershell
python -m ai_objective_index.real_pypi_install_verify
python -m ai_objective_index.real_pypi_release_audit
python -m ai_objective_index.mcp_registry_after_pypi_gate
```

MCP Registry submission remains a later gated package.
