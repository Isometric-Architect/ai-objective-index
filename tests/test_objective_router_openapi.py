import json
from pathlib import Path

from ai_objective_index.vnext.objective_router_openapi import save_objective_router_openapi


def test_vnext_openapi_file_generated():
    path = save_objective_router_openapi()
    assert Path(path).exists()
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    assert "/v1/objectives/route" in payload["paths"]
    audit = json.loads(Path("public_launch/wave5/OBJECTIVE_ROUTER_OPENAPI_AUDIT.json").read_text(encoding="utf-8"))
    assert audit["read_only"] is True
    assert audit["probe_execution"] is False
