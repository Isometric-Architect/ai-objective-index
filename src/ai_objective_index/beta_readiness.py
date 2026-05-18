from __future__ import annotations

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import mcp_tools
from .datascope_qa import DEFAULT_OUTPUT_PATH, run_datascope_qa, save_datascope_qa_results


DEFAULT_REPORT_PATH = Path("data/generated/beta_readiness_report_v0_2.md")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_or_create_qa() -> dict[str, Any]:
    path = _repo_root() / DEFAULT_OUTPUT_PATH
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    results = run_datascope_qa()
    save_datascope_qa_results(results)
    return results


def _token(condition: bool, checked: bool = True) -> str:
    if not checked:
        return "NOT_CHECKED"
    return "PASS" if condition else "HOLD"


def _api_probe() -> dict[str, Any]:
    try:
        from fastapi.testclient import TestClient

        from .api import app

        client = TestClient(app)
        status = client.get("/status")
        search = client.get("/search", params={"query": "api", "data_scope": "integrated", "limit": 5})
        curated = client.get("/search", params={"query": "api", "data_scope": "curated", "limit": 5})
        public_beta = client.get("/search", params={"query": "api", "data_scope": "public_beta", "limit": 5})
        registry = client.get("/search", params={"query": "mcp", "data_scope": "mcp_registry", "limit": 5})
        public_beta_mcp = client.get("/search", params={"query": "mcp", "data_scope": "public_beta_mcp", "limit": 5})
        ok = (
            status.status_code == 200
            and search.status_code == 200
            and curated.status_code == 200
            and public_beta.status_code == 200
            and registry.status_code == 200
            and public_beta_mcp.status_code == 200
        )
        payload = status.json() if status.status_code == 200 else {}
        return {
            "token": _token(
                ok
                and payload.get("default_data_scope") == "sample"
                and payload.get("live_network_enabled") is False
            ),
            "details": "API data_scope probe passed." if ok else "API data_scope probe failed.",
        }
    except Exception as exc:
        return {"token": "HOLD", "details": f"API probe failed: {exc}"}


def _mcp_probe() -> dict[str, Any]:
    try:
        sample = mcp_tools.search_objectives("api", data_scope="sample", limit=3)
        generated = mcp_tools.search_objectives("api", data_scope="generated", limit=3)
        integrated = mcp_tools.search_objectives("api", data_scope="integrated", limit=3)
        curated = mcp_tools.search_objectives("api", data_scope="curated", limit=3)
        public_beta = mcp_tools.search_objectives("api", data_scope="public_beta", limit=3)
        registry = mcp_tools.search_objectives("mcp", data_scope="mcp_registry", limit=3)
        public_beta_mcp = mcp_tools.search_objectives("mcp", data_scope="public_beta_mcp", limit=3)
        ok = (
            sample.get("data_scope") == "sample"
            and generated.get("data_scope") == "generated"
            and integrated.get("data_scope") == "integrated"
            and curated.get("data_scope") == "curated"
            and public_beta.get("data_scope") == "public_beta"
            and registry.get("data_scope") == "mcp_registry"
            and public_beta_mcp.get("data_scope") == "public_beta_mcp"
            and sample.get("read_only") is True
            and "payment" in sample.get("forbidden_actions", [])
        )
        return {
            "token": _token(ok),
            "details": "MCP data_scope probes passed." if ok else "MCP data_scope probe returned unexpected data.",
        }
    except Exception as exc:
        return {"token": "HOLD", "details": f"MCP probe failed: {exc}"}


def _hf_demo_probe() -> dict[str, Any]:
    try:
        app_path = _repo_root() / "hf_demo" / "app.py"
        spec = importlib.util.spec_from_file_location("hf_demo_app_beta_readiness", app_path)
        if spec is None or spec.loader is None:
            return {"token": "HOLD", "details": "HF demo app.py could not be loaded."}
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sample = module.run_demo_query("api", limit=2, data_scope="sample")
        integrated = module.run_demo_query("api", limit=2, data_scope="integrated")
        public_beta = module.run_demo_query("api", limit=2, data_scope="public_beta")
        public_beta_mcp = module.run_demo_query("mcp", limit=2, data_scope="public_beta_mcp")
        ok = (
            sample[2]["read_only"] is True
            and integrated[2]["data_scope"] == "integrated"
            and public_beta[2]["data_scope"] == "public_beta"
            and public_beta_mcp[2]["data_scope"] == "public_beta_mcp"
        )
        return {
            "token": _token(ok),
            "details": "HF demo is import-safe and data_scope-aware." if ok else "HF demo probe failed.",
        }
    except Exception as exc:
        return {"token": "HOLD", "details": f"HF demo probe failed: {exc}"}


def _productization_docs_probe() -> dict[str, Any]:
    root = _repo_root()
    docs = [
        root / "docs" / "productization_mode.md",
        root / "docs" / "research_to_product_bridge.md",
        root / "docs" / "public_claim_policy.md",
    ]
    ok = all(path.exists() for path in docs)
    if not ok:
        readme = (root / "README.md").read_text(encoding="utf-8")
        ok = "Productization" in readme
    return {
        "token": _token(ok),
        "details": "Productization Mode docs are present." if ok else "Productization Mode docs are missing.",
    }


def build_beta_readiness_report() -> tuple[str, dict[str, Any]]:
    qa = _load_or_create_qa()
    scopes = qa["scopes"]
    api = _api_probe()
    mcp = _mcp_probe()
    hf_demo = _hf_demo_probe()
    productization_docs = _productization_docs_probe()

    sample_ok = scopes["sample"]["object_count"] > 0
    generated_ok = (
        scopes["generated"]["object_count"] >= 3
        and scopes["generated"]["generated_unverified_status_ok"]
    )
    integrated_ok = scopes["integrated"]["object_count"] >= (
        scopes["sample"]["object_count"] + scopes["generated"]["object_count"]
    )
    curated_scope_ok = "curated" in scopes and "public_beta" in scopes
    registry_scope_ok = "mcp_registry" in scopes and "public_beta_mcp" in scopes
    coverage_ok = all("source_trace_coverage" in scopes[scope] for scope in scopes)
    no_network_ok = qa.get("live_network_used") is False
    eval_report_ok = (_repo_root() / "data" / "generated" / "integrated_eval_results_v0_2.json").exists()
    source_trace_ok = coverage_ok and all(scopes[scope]["trace_count"] >= 0 for scope in scopes)

    rows = [
        ("sample scope", _token(sample_ok), f"{scopes['sample']['object_count']} objects"),
        ("generated scope", _token(generated_ok), f"{scopes['generated']['object_count']} objects, EXTRACTED_UNVERIFIED retained"),
        ("integrated scope", _token(integrated_ok), f"{scopes['integrated']['object_count']} objects"),
        (
            "curated/public_beta scopes",
            _token(curated_scope_ok),
            f"curated={scopes.get('curated', {}).get('object_count', 0)} objects; public_beta={scopes.get('public_beta', {}).get('object_count', 0)} objects",
        ),
        (
            "mcp_registry/public_beta_mcp scopes",
            _token(registry_scope_ok),
            f"mcp_registry={scopes.get('mcp_registry', {}).get('object_count', 0)} objects; public_beta_mcp={scopes.get('public_beta_mcp', {}).get('object_count', 0)} objects",
        ),
        ("source trace coverage", _token(coverage_ok), "coverage metric exists for every scope"),
        ("no live network", _token(no_network_ok), "No live crawling or network fetch used"),
        ("API data_scope", api["token"], api["details"]),
        ("MCP data_scope", mcp["token"], mcp["details"]),
        ("HF demo", hf_demo["token"], hf_demo["details"]),
        ("eval/report artifacts", _token(eval_report_ok), "integrated eval output present" if eval_report_ok else "integrated eval output missing"),
        ("Productization Mode", productization_docs["token"], productization_docs["details"]),
    ]
    overall = "PASS" if all(row[1] == "PASS" for row in rows) else "HOLD"
    metadata = {
        "overall": overall,
        "rows": rows,
        "api": api,
        "mcp": mcp,
        "hf_demo": hf_demo,
        "source_trace_ok": source_trace_ok,
    }

    lines = [
        "# AOI Beta Readiness Report v0.2",
        "",
        f"Generated at: `{datetime.now(UTC).isoformat()}`",
        "",
        "## What Package 6D Checks",
        "",
        "Package 6D checks that `sample`, `generated`, `integrated`, `curated`, `public_beta`, `mcp_registry`, and `public_beta_mcp` data scopes are visible across local Core, MCP, REST API, Hugging Face demo, eval, reports, and docs.",
        "",
        "## Current AOI Status",
        "",
        f"Overall readiness token: `{overall}`",
        "",
        "AOI remains read-only and local-data-only. No live crawling is performed.",
        "",
        "## Productization Mode Summary",
        "",
        "Productization Mode allows implementation, algorithmization, MCP/API engines, GitHub work, MVPs, and commercialization experiments. Public product, security, legal, market, or readiness claims still require product evidence.",
        "",
        "## Scope Readiness Table",
        "",
        "| Check | Token | Evidence |",
        "| --- | --- | --- |",
    ]
    for name, token, detail in rows:
        lines.append(f"| {name} | {token} | {detail} |")
    lines.extend(
        [
            "",
            "## API/MCP Readiness",
            "",
            f"- API: `{api['token']}` - {api['details']}",
            f"- MCP: `{mcp['token']}` - {mcp['details']}",
            "",
            "## HF Demo Readiness",
            "",
            f"- HF demo: `{hf_demo['token']}` - {hf_demo['details']}",
            "",
            "## Eval/Report Readiness",
            "",
            f"- Integrated eval artifact: `{_token(eval_report_ok)}`",
            "- `data/generated/datascope_qa_results_v0_2.json` is generated by Package 6D.",
            "",
            "## Source Trace Readiness",
            "",
            f"- Source trace coverage metric exists for every scope: `{_token(source_trace_ok)}`",
            "- Generated records must remain `EXTRACTED_UNVERIFIED`.",
            "",
            "## Known Limits",
            "",
            "- This is local beta readiness, not a public release certification.",
            "- Product claims require product evidence.",
            "- Source traces support fields but do not guarantee correctness, completeness, legal sufficiency, or currentness.",
            "",
            "## Not Implemented",
            "",
            "- live crawling",
            "- network fetch",
            "- external LLM APIs",
            "- Hugging Face publishing",
            "- community posting",
            "- payment, booking, login, email sending, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification",
            "",
            "## Recommended Next Package",
            "",
            "Package 6E should focus on packaging, release checks, and explicit external validation planning without enabling live crawling or external actions.",
        ]
    )
    return "\n".join(lines) + "\n", metadata


def write_beta_readiness_report(path: str | Path = DEFAULT_REPORT_PATH) -> Path:
    markdown, _metadata = build_beta_readiness_report()
    destination = Path(path)
    if not destination.is_absolute():
        destination = Path.cwd() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown, encoding="utf-8")
    return destination


def main() -> None:
    path = write_beta_readiness_report()
    _markdown, metadata = build_beta_readiness_report()
    print(f"Saved beta readiness report: {path}")
    print(f"beta_readiness={metadata['overall']}")


if __name__ == "__main__":
    main()
