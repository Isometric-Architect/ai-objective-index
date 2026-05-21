# Package 8Q-A: Local Build Tool Install + Dist Build + Twine Check

Package 8Q-A prepares AI Objective Index for a future PyPI/TestPyPI upload by checking local packaging tools, building local distribution artifacts, running `twine check`, and running a local install smoke test.

It does not upload to TestPyPI, upload to PyPI, submit to MCP Registry, post to communities, request tokens, print tokens, store tokens, or commit tokens.

## Commands

```powershell
python -m ai_objective_index.local_build_tools --check
python -m ai_objective_index.local_build_tools --install
python -m ai_objective_index.dist_build_runner
python -m ai_objective_index.local_install_smoke
python -m ai_objective_index.pypi_readiness_refresh
```

Run `--install` only when local `build` or `twine` is missing.

## Expected HOLD State

After local build and twine check pass, readiness should normally move to `HOLD_TESTPYPI_ACCOUNT_REQUIRED`. That means the next step is a human TestPyPI account/token setup, not an automated upload.

## Claim Boundary

Package 8Q-A does not change AOI's public claim boundary. AOI remains read-only, not verified, not security certified, not a quality guarantee, and not purchasing advice.
