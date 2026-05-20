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
