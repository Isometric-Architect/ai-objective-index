from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from ai_objective_index.models import ActionObject, ObjectStatus, SourceTrace


REGISTRY_BASE = "https://registry.modelcontextprotocol.io"


def _string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _body(record: dict[str, Any]) -> dict[str, Any]:
    nested = record.get("server")
    if isinstance(nested, dict):
        merged = dict(nested)
        if "_meta" in record:
            merged["_meta"] = record["_meta"]
        if "fixture_only" in record:
            merged["fixture_only"] = record["fixture_only"]
        return merged
    return record


def _name(record: dict[str, Any]) -> str:
    record = _body(record)
    return (
        _string(record.get("name"))
        or _string(record.get("serverName"))
        or _string(record.get("server_name"))
        or _string(record.get("id"))
        or "unknown-mcp-server"
    )


def _object_id(name: str, version: str | None = None) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    version_suffix = ""
    if version:
        version_suffix = "-" + re.sub(r"[^a-zA-Z0-9]+", "-", version).strip("-").lower()
    return f"mcp-registry-{normalized or 'unknown'}{version_suffix}"


def _repository(record: dict[str, Any]) -> str:
    record = _body(record)
    repository = record.get("repository") or record.get("repo") or record.get("source")
    if isinstance(repository, dict):
        return _string(repository.get("url") or repository.get("html_url"))
    return _string(repository)


def _homepage(record: dict[str, Any]) -> str:
    record = _body(record)
    return _string(record.get("homepage") or record.get("website") or record.get("url"))


def _docs(record: dict[str, Any]) -> str:
    record = _body(record)
    return _string(record.get("documentation") or record.get("docs") or record.get("docsUrl") or record.get("readmeUrl"))


def derive_capabilities(record: dict[str, Any]) -> list[str]:
    record = _body(record)
    text = " ".join(
        [
            _name(record),
            _string(record.get("description")),
            " ".join(str(item) for item in _list(record.get("tags"))),
            " ".join(str(item) for item in _list(record.get("capabilities"))),
        ]
    ).lower()
    capabilities: set[str] = {"mcp_server"}
    keyword_map = {
        "browser": "browser_automation",
        "search": "web_search",
        "document": "document_extraction",
        "ocr": "ocr",
        "vector": "vector_database",
        "database": "database",
        "code": "code_execution",
        "runner": "code_execution",
        "github": "github_integration",
    }
    for keyword, capability in keyword_map.items():
        if keyword in text:
            capabilities.add(capability)
    for item in _list(record.get("capabilities")):
        if isinstance(item, str) and item.strip():
            capabilities.add(item.strip().lower().replace(" ", "_"))
    return sorted(capabilities)


def derive_integration_methods(record: dict[str, Any]) -> list[str]:
    record = _body(record)
    methods: set[str] = set()
    for package in _list(record.get("packages")):
        if isinstance(package, dict):
            registry = _string(package.get("registry") or package.get("type"))
            name = _string(package.get("name"))
            if registry or name:
                methods.add(":".join(part for part in [registry, name] if part))
        elif package:
            methods.add(_string(package))
    for remote in _list(record.get("remotes")):
        if isinstance(remote, dict):
            methods.add(_string(remote.get("transport") or remote.get("url") or "remote"))
        elif remote:
            methods.add(_string(remote))
    install = record.get("install") or record.get("installation")
    if install:
        methods.add("install_metadata")
    return sorted(methods)


def derive_docs_and_repo(record: dict[str, Any]) -> dict[str, str]:
    record = _body(record)
    repository = _repository(record)
    docs_url = _docs(record)
    homepage = _homepage(record)
    github_url = repository if "github.com" in repository.lower() else ""
    return {
        "repository_url": repository,
        "github_url": github_url,
        "docs_url": docs_url,
        "homepage_url": homepage,
    }


def _registry_source_url(name: str, version: str | None = None) -> str:
    quoted = name.strip("/")
    if version:
        return f"{REGISTRY_BASE}/v0.1/servers/{quoted}/versions/{version}"
    return f"{REGISTRY_BASE}/v0.1/servers/{quoted}/versions/latest"


def _confidence(record: dict[str, Any]) -> float:
    record = _body(record)
    score = 0.55
    if _repository(record):
        score += 0.1
    if _docs(record):
        score += 0.05
    if derive_capabilities(record):
        score += 0.05
    if record.get("fixture_only"):
        score -= 0.1
    return round(max(0.2, min(0.8, score)), 2)


def registry_record_to_action_object(record: dict[str, Any]) -> ActionObject:
    record = _body(record)
    name = _name(record)
    version = _string(record.get("version")) or None
    docs = derive_docs_and_repo(record)
    registry_source = _registry_source_url(name, version)
    source_urls = [
        url
        for url in [
            registry_source,
            docs["repository_url"],
            docs["docs_url"],
            docs["homepage_url"],
        ]
        if url
    ]
    action_object = {
        "object_id": _object_id(name, version),
        "name": name,
        "object_type": "MCPServer",
        "summary": _string(record.get("description")) or "MCP Registry server metadata record.",
        "official_url": docs["repository_url"] or docs["homepage_url"] or registry_source,
        "source_urls": source_urls,
        "capabilities": derive_capabilities(record),
        "categories": ["mcp_server", "mcp_registry"],
        "pricing": {},
        "policies": {"registry_source": "official_mcp_registry_metadata"},
        "docs": {
            "docs_url": docs["docs_url"],
            "repository_url": docs["repository_url"],
            "github_url": docs["github_url"],
            "registry_url": registry_source,
        },
        "status": ObjectStatus.EXTRACTED_UNVERIFIED.value,
        "confidence": _confidence(record),
        "missing_fields": [],
        "last_checked_at": datetime.now(UTC).isoformat(),
        "source_rank": "A",
        "registry_name": name,
        "registry_version": version,
        "integration_methods": derive_integration_methods(record),
        "package_metadata": record.get("packages", []),
        "remote_metadata": record.get("remotes", []),
        "fixture_only": bool(record.get("fixture_only")),
        "supplier_verified": False,
    }
    missing_fields = []
    if not docs["repository_url"] and not docs["homepage_url"]:
        missing_fields.append("repository_or_homepage")
    if not docs["docs_url"]:
        missing_fields.append("docs_url")
    if len(action_object["capabilities"]) <= 1:
        missing_fields.append("clear_capabilities")
    action_object["missing_fields"] = missing_fields
    return ActionObject.model_validate(action_object)


def _trace(
    object_id: str,
    name: str,
    field: str,
    value: Any,
    source_url: str,
    confidence: float,
) -> SourceTrace:
    snippet = _string(value)
    if len(snippet) > 240:
        snippet = snippet[:237] + "..."
    return SourceTrace.model_validate(
        {
            "trace_id": f"trace-{object_id}-{field.replace('.', '-').replace('_', '-')}",
            "object_id": object_id,
            "field": field,
            "source_url": source_url,
            "source_title": f"Official MCP Registry record for {name}",
            "source_snippet": snippet or f"Registry metadata field: {field}",
            "retrieved_at": datetime.now(UTC).isoformat(),
            "confidence": confidence,
            "source_rank": "A",
        }
    )


def registry_record_to_source_traces(record: dict[str, Any]) -> list[SourceTrace]:
    record = _body(record)
    action_object = registry_record_to_action_object(record)
    name = action_object.name
    source_url = action_object.docs.get("registry_url") or _registry_source_url(name)
    confidence = min(0.85, max(0.5, action_object.confidence))
    fields = {
        "name": name,
        "description": record.get("description") or action_object.summary,
        "repository": _repository(record),
        "package": record.get("packages") or record.get("package"),
        "install": record.get("install") or record.get("installation"),
        "capabilities": derive_capabilities(record),
    }
    traces = [
        _trace(action_object.object_id, name, field, value, source_url, confidence)
        for field, value in fields.items()
        if value
    ]
    return traces
