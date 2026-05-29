from __future__ import annotations

from .qira_patch_classifier import stable_id
from .qira_pilot_receipt import QIRABehaviorContract, QIRATaskPacket


FORBIDDEN_BEHAVIOR_MARKERS = [
    "deploy",
    "publish_package",
    "merge",
    "comment_on_pr",
    "mutate_external_repo",
    "use_live_credentials",
    ".pypirc",
    ".env",
]


def build_behavior_contract(task_packet: QIRATaskPacket) -> QIRABehaviorContract:
    return QIRABehaviorContract(
        contract_id=stable_id("qira-contract", task_packet.task_id, task_packet.task_goal),
        task_id=task_packet.task_id,
        expected_behavior=[
            "Classify the local patch scope.",
            "Separate docs/test review signals from release/deploy actions.",
            "Surface CI evidence gaps without treating CI summaries as proof.",
            "Write a reviewer artifact and feedback memory entry only.",
        ],
        non_goals=[
            "No GitHub API calls.",
            "No external repository mutation.",
            "No merge or deploy authorization.",
            "No code-correctness or security certification.",
        ],
        forbidden_behavior=[
            "create_pr",
            "merge",
            "deploy",
            "publish_package",
            "comment_on_pr",
            "mutate_external_repo",
            "use_live_credentials",
        ],
    )


def behavior_contract_detects_forbidden(contract: QIRABehaviorContract, text: str, changed_files: list[str] | None = None) -> bool:
    lowered = text.lower()
    paths = " ".join(changed_files or []).lower()
    markers = [item.lower() for item in contract.forbidden_behavior] + FORBIDDEN_BEHAVIOR_MARKERS
    return any(marker and (marker in lowered or marker in paths) for marker in markers)
