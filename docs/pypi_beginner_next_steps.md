# PyPI Beginner Next Steps

PyPI is where Python packages are published. TestPyPI is the practice version. Use TestPyPI first.

## Beginner Path

1. Create a TestPyPI account.
2. Verify your email.
3. Create a TestPyPI API token.
4. Do not paste the token into ChatGPT/Codex chat.
5. Do not save the token in this repo.
6. Do not commit `.pypirc` or any token file.
7. Upload to TestPyPI manually only after local build, `twine check`, and local install smoke pass.
8. Install from TestPyPI in a clean environment.
9. Only then create a real PyPI account/token.
10. Upload to real PyPI manually after the TestPyPI path works.

## Important

TestPyPI and PyPI are separate accounts. A token may only be shown once. Keep it private.

Package 8Q-A resumed does not upload anything. A PyPI/TestPyPI token is not needed until a later explicit upload package.
