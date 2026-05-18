from pathlib import Path

from ai_objective_index.public_beta_realdata_packager import create_public_beta_realdata_pack


def test_public_beta_v0_2_assets_exist_after_packaging():
    create_public_beta_realdata_pack()
    root = Path.cwd()

    assert (root / "release/public_beta_v0_2/README_PUBLIC_BETA_v0_2.md").exists()
    assert (root / "release/public_beta_v0_2/REAL_DATA_SUMMARY_v0_2.md").exists()
    assert (root / "hf_dataset/README.md").exists()
    assert (root / "hf_dataset/mcp_registry_beta_candidates.jsonl").exists()
    assert (root / "hf_dataset/mcp_registry_source_traces.jsonl").exists()
    assert (root / "reports/mcp_server_objective_index_v0_2.md").exists()
    assert (root / "reports/source_trace_quality_report_v0_2.md").exists()
    assert (root / "data/generated/final_preflight_result_v0_2.json").exists()

    dataset_card = (root / "hf_dataset/README.md").read_text(encoding="utf-8").lower()
    assert "not verified" in dataset_card
    assert "not security certified" in dataset_card
