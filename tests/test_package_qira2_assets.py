from pathlib import Path


def test_qira2_docs_exist():
    for path in [
        "docs/qira2_task_packet_intake.md",
        "docs/qira_local_packet_cli.md",
    ]:
        assert Path(path).exists(), path


def test_qira2_outputs_exist():
    for path in [
        "public_launch/qira2/QIRA2_SAMPLE_TASK_PACKET.json",
        "public_launch/qira2/QIRA2_PACKET_INTAKE_RESULT.json",
        "public_launch/qira2/QIRA2_RELEASE_GATE_REPORT.json",
        "public_launch/qira2/QIRA2_NEXT_STEPS.md",
        "public_launch/qira2/QIRA_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert Path(path).exists(), path
