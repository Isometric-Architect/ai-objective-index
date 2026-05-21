# Next 8Q-A Resume Instructions

Next package: 8Q-A Local Build Tool Install + Dist Build + Twine Check.

Before resuming:

- Distribution gate decision: `HOLD_VERSION_DECISION`
- Version decision: choose `0.3.0` or `0.3.0a1` before upload-oriented packages.

8Q-A will:

1. Install/check `build` and `twine` locally if needed.
2. Build wheel and sdist locally.
3. Run `twine check`.
4. Run local install smoke tests.
5. Refresh PyPI/MCP Registry readiness.

8Q-A will not upload to TestPyPI or PyPI.

The user does not need a PyPI token yet. A token is needed only in a later explicit TestPyPI upload package. Do not paste tokens into chat, save tokens in the repository, or commit `.pypirc` files.
