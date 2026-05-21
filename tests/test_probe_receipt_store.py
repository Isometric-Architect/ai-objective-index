from ai_objective_index.vnext.probe_card import ProbePlan, ProbeResult
from ai_objective_index.vnext.probe_receipt_store import ProbeReceiptStore
from ai_objective_index.vnext.probe_runner import run_probe_plan


def test_probe_receipt_store_appends_and_lists(tmp_path):
    store = ProbeReceiptStore(tmp_path / "probes.jsonl", tmp_path / "probe_index.json")
    receipt = run_probe_plan(ProbePlan())
    record = store.append_probe_receipt(receipt)
    assert record["token_printed"] is False
    assert store.get_probe_receipt(receipt.receipt_id or "") is not None


def test_probe_receipt_store_redacts_token_like_strings(tmp_path):
    store = ProbeReceiptStore(tmp_path / "probes.jsonl", tmp_path / "probe_index.json")
    receipt = run_probe_plan(ProbePlan())
    receipt.probe_results.append(
        ProbeResult(
            probe_id="probe-token",
            capability_id="capability:test",
            result="HOLD_INSUFFICIENT_EVIDENCE",
            findings=["hf_abcdefghijklmnopqrstuvwxyz1234567890TOKENLIKE"],
        )
    )
    record = store.append_probe_receipt(receipt)
    assert record["token_redacted"] is True


def test_probe_memory_summarizes_results(tmp_path):
    store = ProbeReceiptStore(tmp_path / "probes.jsonl", tmp_path / "probe_index.json")
    receipt = run_probe_plan(ProbePlan())
    store.append_probe_receipt(receipt)
    memory = store.build_capability_probe_memory("capability:not-found")
    assert memory.can_verify is False
    assert memory.can_certify_security is False
