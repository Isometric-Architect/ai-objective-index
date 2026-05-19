from __future__ import annotations

import json
from pathlib import Path

from .api import app


def export_openapi(path: str | Path = "api/openapi.json") -> Path:
    destination = Path(path)
    if not destination.is_absolute():
        destination = Path.cwd() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def main() -> None:
    path = export_openapi()
    print(f"Exported OpenAPI spec: {path}")


if __name__ == "__main__":
    main()

