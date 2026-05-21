# PyPI Resume After vNext

After Package 9F, the next package can resume 8Q-A local build checks.

8Q-A should:

- check/install `build` and `twine`;
- build local wheel and sdist;
- run `twine check`;
- run local install smoke;
- refresh PyPI readiness.

8Q-A must not upload to TestPyPI or PyPI. No PyPI token is needed yet.

Before an upload-oriented package, choose whether vNext uses `0.3.0` or `0.3.0a1`.
