# Package 8Q-A Resumed: vNext Local Build + Twine Check

Package 8Q-A resumed applies the vNext build candidate version `0.3.0a1`, builds local wheel/sdist artifacts, runs `twine check`, runs a local install smoke, and refreshes PyPI/MCP Registry readiness.

It does not upload to TestPyPI or PyPI, does not submit to MCP Registry, does not ask for tokens, and does not create `.pypirc`.

## Commands

```bash
python -m ai_objective_index.version_apply_gate --dry-run
python -m ai_objective_index.version_apply_gate --apply 0.3.0a1
python -m ai_objective_index.local_build_tools --check
python -m ai_objective_index.local_build_tools --install
python -m ai_objective_index.dist_build_runner
python -m ai_objective_index.local_install_smoke
python -m ai_objective_index.pypi_readiness_refresh
python -m ai_objective_index.mcp_registry_readiness_refresh
```

The expected post-build state is still conservative: PyPI readiness should HOLD for TestPyPI account/token steps, and MCP Registry readiness should HOLD until a real PyPI package exists.
