import json
from pathlib import Path

from ai_objective_index.portfolio.datacapsule_pilot_packager import RECEIPT_PATH, package_datacapsule_pilot
from ai_objective_index.portfolio.roe10_datacapsule_pilot_gate import GATE_RESULT_PATH, run_roe10_gate


def test_roe10_gate_passes_safe_sample():
    package_datacapsule_pilot(sample=True)
    result = run_roe10_gate(write_result=True)

    assert result["decision"] == "PASS_FIRST_DATACAPSULE_PILOT_RECEIPT_READY"
    assert result["redaction_decision"] == "PASS_REDACTED"
    assert result["raw_content_inspected"] is False
    assert result["external_network_used"] is False
    assert Path(GATE_RESULT_PATH).exists()


def test_roe10_gate_blocks_overclaim_fixture():
    package_datacapsule_pilot(sample=True)
    path = Path(RECEIPT_PATH)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["corpus_manifest"]["corpus_label"] = "eval clean dataset safe"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        result = run_roe10_gate(write_result=False, ensure_sample=False)

        assert result["decision"] == "BLOCK_OVERCLAIM"
    finally:
        package_datacapsule_pilot(sample=True)
        run_roe10_gate(write_result=True)


def test_roe10_gate_blocks_raw_content_inspection_fixture():
    package_datacapsule_pilot(sample=True)
    path = Path(RECEIPT_PATH)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["raw_content_inspected"] = True
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        result = run_roe10_gate(write_result=False, ensure_sample=False)

        assert result["decision"] == "BLOCK_RAW_CONTENT_INSPECTION"
    finally:
        package_datacapsule_pilot(sample=True)
        run_roe10_gate(write_result=True)


def test_roe10_gate_blocks_external_network_fixture():
    package_datacapsule_pilot(sample=True)
    path = Path(RECEIPT_PATH)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["external_network_used"] = True
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        result = run_roe10_gate(write_result=False, ensure_sample=False)

        assert result["decision"] == "BLOCK_EXTERNAL_NETWORK"
    finally:
        package_datacapsule_pilot(sample=True)
        run_roe10_gate(write_result=True)
