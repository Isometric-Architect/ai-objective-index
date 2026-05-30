# AOI PyPI Upload Final

The final PyPI upload path is intentionally narrow:

1. Run `python -m pytest`.
2. Run `python -m ai_objective_index.aoi_030a2_final_preflight`.
3. Run `python -m ai_objective_index.aoi_030a2_build_verify`.
4. Run `python -m ai_objective_index.aoi_030a2_final_pypi_upload_gate`.
5. If the gate is ready, set `$env:AOI_REAL_PYPI_UPLOAD_CONFIRM="YES"`.
6. Run `python -m ai_objective_index.aoi_030a2_final_pypi_upload_runner --execute`.
7. Enter `__token__` and the PyPI token only into the local `twine` prompt.
8. Run `python -m ai_objective_index.aoi_030a2_final_pypi_verify`.

Do not pass tokens on the command line, paste tokens into chat, store tokens in files, create `.pypirc`, overwrite an existing version, delete or yank `0.3.0a1`, or commit dist files by default.

If `0.3.0a2` already exists on PyPI, stop upload and verify the existing package before deciding whether a later version is needed.

