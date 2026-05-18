import json

from ai_objective_index.openapi_export import export_openapi


def test_export_openapi_writes_api_openapi_json():
    path = export_openapi()

    assert path.name == "openapi.json"
    assert path.parent.name == "api"
    assert path.exists()

    payload = json.loads(path.read_text(encoding="utf-8"))
    paths = payload["paths"]
    assert "/search" in paths
    assert "/status" in paths
    assert "/objects/{object_id}" in paths
    assert "/compare" in paths
    assert "/decision-receipt" in paths

