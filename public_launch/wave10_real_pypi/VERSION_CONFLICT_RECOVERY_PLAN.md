# Version Conflict Recovery Plan

If version `0.3.0a1` already exists on real PyPI, or the upload partially succeeds, do not retry the same files blindly.

Safe response:

1. Confirm whether the wheel or sdist is already present on PyPI.
2. Do not delete or overwrite the published file as a normal workflow.
3. If a fix is needed after real PyPI upload, bump to `0.3.0a2`.
4. Rebuild wheel/sdist from the fixed source.
5. Run `twine check` again.
6. Keep release notes clear about the alpha build.

The PyPI package remains a public beta/alpha distribution artifact, not a verification, security certification, quality guarantee, product-readiness claim, or purchasing advice.
