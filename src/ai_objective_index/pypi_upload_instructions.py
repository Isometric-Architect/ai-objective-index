from __future__ import annotations

from pathlib import Path


WAVE2_DIR = Path("public_launch") / "wave2"
TESTPYPI_PATH = WAVE2_DIR / "TESTPYPI_UPLOAD_INSTRUCTIONS.md"
PYPI_PATH = WAVE2_DIR / "PYPI_UPLOAD_INSTRUCTIONS.md"
MCP_PATH = WAVE2_DIR / "MCP_REGISTRY_PUBLISH_INSTRUCTIONS.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def write_pypi_upload_instructions() -> dict[str, str]:
    testpypi = """# TestPyPI Upload Instructions

1. Create a TestPyPI account if needed.
2. Create a scoped upload API token.
3. Do not paste the token into ChatGPT/Codex chat.
4. Do not save the token in this repository.
5. Build locally:

```powershell
python -m ai_objective_index.pypi_publish_readiness
```

6. Upload manually:

```powershell
python -m twine upload --repository testpypi dist/*
```

7. Verify the TestPyPI package page.
8. Install from TestPyPI in a clean environment if desired.

No upload is performed by Package 8P.
"""
    pypi = """# PyPI Upload Instructions

1. Create or open the PyPI project owner account.
2. Create a scoped API token for `ai-objective-index`.
3. Do not paste the token into ChatGPT/Codex chat.
4. Do not commit the token.
5. Confirm:
   - `python -m ai_objective_index.package_metadata_audit`
   - `python -m ai_objective_index.pypi_publish_readiness`
   - `python -m ai_objective_index.no_secrets_audit`
   - `python -m ai_objective_index.launch_claim_guard`
6. Upload manually:

```powershell
python -m twine upload dist/*
```

7. Verify the package page and console scripts.
8. Rerun MCP Registry readiness.

Package 8P does not upload to PyPI.
"""
    mcp = """# MCP Registry Publish Instructions

1. Confirm PyPI package `ai-objective-index` version `0.3.0a1` is public after the explicit PyPI upload package.
2. Confirm README contains:

```html
<!-- mcp-name: io.github.isometric-architect/ai-objective-index -->
```

3. Confirm `.mcp/server.json` uses `registryType: pypi`.
4. Run:

```powershell
python -m ai_objective_index.mcp_registry_publish_readiness
```

5. Submit only if readiness is `PASS_READY_TO_SUBMIT`.
6. Set explicit confirmation only when ready:

```powershell
$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"
```

7. Then use the dedicated MCP publisher flow.

Package 8P does not submit to MCP Registry.
"""
    return {
        "testpypi": str(_write(TESTPYPI_PATH, testpypi)),
        "pypi": str(_write(PYPI_PATH, pypi)),
        "mcp_registry": str(_write(MCP_PATH, mcp)),
    }


def main() -> None:
    paths = write_pypi_upload_instructions()
    print("pypi_upload_instructions: wrote TestPyPI, PyPI, and MCP Registry instructions")
    for key, value in paths.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
