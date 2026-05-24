from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CommandRisk = Literal["LOW", "MEDIUM", "HIGH", "BLOCK"]

SAFE_COMMAND_PATTERNS = [
    re.compile(r"^(python\s+-m\s+pytest|pytest)(\s|$)", re.I),
    re.compile(r"^python\s+-m\s+unittest(\s|$)", re.I),
    re.compile(r"^(python\s+-m\s+ruff|ruff)\s+check(\s|$)", re.I),
    re.compile(r"^(python\s+-m\s+mypy|mypy)(\s|$)", re.I),
]
BLOCK_COMMAND_PATTERNS = [
    re.compile(r"\b(twine\s+upload|mcp-publisher\s+publish|npm\s+publish)\b", re.I),
    re.compile(r"\b(git\s+push|gh\s+release|gh\s+repo)\b", re.I),
    re.compile(r"\b(curl|wget|Invoke-WebRequest|iwr)\b", re.I),
    re.compile(r"\bRemove-Item\b.*\b-Recurse\b", re.I),
    re.compile(r"\brm\s+-rf\b", re.I),
    re.compile(r"\bpowershell\b.*\s-enc(odedcommand)?\b", re.I),
]
HOLD_COMMAND_PATTERNS = [
    re.compile(r"\b(pip\s+install|python\s+-m\s+pip\s+install|npm\s+install|docker\s+run|docker\s+compose)\b", re.I),
    re.compile(r"\b(playwright\s+install|browser|login|auth)\b", re.I),
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


class TestCommandRecord(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_TestCommandRecord/v0.1", alias="schema")
    command: str
    risk: CommandRisk
    review_status: str
    reasons: list[str] = Field(default_factory=list)
    executed_by_qira: bool = False


class TestCommandContract(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="QIRA_TestCommandContract/v0.1", alias="schema")
    decision: str
    commands: list[TestCommandRecord]
    command_count: int
    allowed_execution: str = "record_only_not_executed"
    block_reasons: list[str] = Field(default_factory=list)
    hold_reasons: list[str] = Field(default_factory=list)
    external_actions_performed: bool = False
    commands_executed: bool = False
    token_printed: bool = False
    generated_at: str = Field(default_factory=_timestamp)


def classify_test_command(command: str) -> TestCommandRecord:
    stripped = command.strip()
    if not stripped:
        return TestCommandRecord(command=command, risk="MEDIUM", review_status="HOLD_EMPTY_COMMAND", reasons=["empty command"])
    for pattern in BLOCK_COMMAND_PATTERNS:
        if pattern.search(stripped):
            return TestCommandRecord(
                command=command,
                risk="BLOCK",
                review_status="BLOCK_EXTERNAL_OR_DESTRUCTIVE_COMMAND",
                reasons=["command can publish, push, fetch network, remove recursively, or use encoded shell"],
            )
    for pattern in HOLD_COMMAND_PATTERNS:
        if pattern.search(stripped):
            return TestCommandRecord(
                command=command,
                risk="HIGH",
                review_status="HOLD_COMMAND_REVIEW_REQUIRED",
                reasons=["command may install dependencies, launch containers, browser flows, login, or auth"],
            )
    for pattern in SAFE_COMMAND_PATTERNS:
        if pattern.search(stripped):
            return TestCommandRecord(
                command=command,
                risk="LOW",
                review_status="PASS_RECORD_ONLY_SAFE_PATTERN",
                reasons=["recognized local test/static-check command pattern"],
            )
    return TestCommandRecord(
        command=command,
        risk="MEDIUM",
        review_status="HOLD_UNRECOGNIZED_COMMAND",
        reasons=["unrecognized command is recorded but not executed"],
    )


def build_test_command_contract(commands: list[str] | None = None) -> TestCommandContract:
    records = [classify_test_command(command) for command in (commands or [])]
    block_reasons: list[str] = []
    hold_reasons: list[str] = []
    for record in records:
        if record.risk == "BLOCK":
            block_reasons.extend(f"{record.command}: {reason}" for reason in record.reasons)
        elif record.risk in {"HIGH", "MEDIUM"}:
            hold_reasons.extend(f"{record.command}: {reason}" for reason in record.reasons)
    if block_reasons:
        decision = "BLOCK_TEST_COMMAND_CONTRACT"
    elif not records:
        decision = "HOLD_TEST_COMMAND_MISSING"
        hold_reasons.append("No test commands were recorded.")
    elif hold_reasons:
        decision = "HOLD_TEST_COMMAND_REVIEW"
    else:
        decision = "PASS_TEST_COMMAND_CONTRACT"
    return TestCommandContract(
        decision=decision,
        commands=records,
        command_count=len(records),
        block_reasons=block_reasons,
        hold_reasons=hold_reasons,
    )
