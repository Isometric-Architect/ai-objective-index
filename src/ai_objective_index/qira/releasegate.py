from __future__ import annotations

import hashlib
import re
from typing import Iterable

from .models import (
    ActionLicense,
    BehaviorContract,
    PatchCandidate,
    PatchReceipt,
    QiraReleaseGateReport,
    ResidualLedger,
    ValidatorPacket,
)


UNSUPPORTED_CLAIM_PATTERNS = [
    re.compile(r"\bverified\b", re.I),
    re.compile(r"\bsafe\b", re.I),
    re.compile(r"\bsecurity\s+certified\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\bproduction[- ]ready\b", re.I),
    re.compile(r"\bdeployment\s+approved\b", re.I),
    re.compile(r"\blegal\s+compliance\b", re.I),
    re.compile(r"\baction\s+authorized\b", re.I),
]

PATH_ESCAPE_PATTERNS = [
    re.compile(r"(^|[\\/])\.\.([\\/]|$)"),
    re.compile(r"^[A-Za-z]:[\\/]"),
    re.compile(r"^/"),
]


def _stable_id(prefix: str, *parts: object) -> str:
    text = "::".join(str(part) for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def build_behavior_contract(task: str, expected_behavior: Iterable[str] | None = None) -> BehaviorContract:
    expected = list(expected_behavior or [])
    return BehaviorContract(
        contract_id=_stable_id("qira-contract", task, expected),
        task=task,
        expected_behavior=expected,
    )


def build_validator_packet(contract: BehaviorContract) -> ValidatorPacket:
    return ValidatorPacket(
        validator_id=_stable_id("qira-validator", contract.contract_id),
        contract_id=contract.contract_id,
        checks=[
            "behavior_contract_present",
            "patch_scope_lint",
            "forbidden_change_check",
            "unsupported_claim_check",
            "test_evidence_check",
            "action_license_noninflation",
        ],
    )


def _path_escape_findings(paths: Iterable[str]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        normalized = path.replace("\\", "/")
        if any(pattern.search(normalized) for pattern in PATH_ESCAPE_PATTERNS):
            findings.append(path)
    return findings


def _forbidden_change_findings(contract: BehaviorContract, patch: PatchCandidate) -> list[str]:
    findings = _path_escape_findings(patch.changed_files)
    lowered_forbidden = [item.lower() for item in contract.forbidden_changes]
    for path in patch.changed_files:
        lowered = path.lower()
        if any(marker in lowered for marker in lowered_forbidden):
            findings.append(path)
    return sorted(set(findings))


def detect_unsupported_claims(claims: Iterable[str]) -> list[str]:
    findings: list[str] = []
    for claim in claims:
        if any(pattern.search(claim) for pattern in UNSUPPORTED_CLAIM_PATTERNS):
            findings.append(claim)
    return findings


def build_residual_ledger(contract: BehaviorContract, patch: PatchCandidate) -> ResidualLedger:
    residuals: list[str] = []
    missing_evidence: list[str] = []
    if not contract.expected_behavior:
        missing_evidence.append("expected_behavior")
        residuals.append("Behavior contract has no expected behavior clauses.")
    if not patch.changed_files:
        missing_evidence.append("changed_files")
        residuals.append("Patch candidate does not list changed files.")
    if not patch.test_summary:
        missing_evidence.append("test_summary")
        residuals.append("Patch candidate does not include a local test summary.")
    if not patch.tests_passed:
        residuals.append("Local or fixture tests are not recorded as passed.")
    if patch.evidence_origin in {"unknown", "self_reported"}:
        missing_evidence.append("independent_or_fixture_evidence")
        residuals.append("Evidence origin is weak; route cannot be inflated to merge or deploy readiness.")

    forbidden = _forbidden_change_findings(contract, patch)
    unsupported_claims = detect_unsupported_claims(patch.declared_claims)
    if forbidden:
        decision = "BLOCK_PATCH_PATH_ESCAPE" if _path_escape_findings(forbidden) else "BLOCK_FORBIDDEN_CHANGE"
    elif unsupported_claims:
        decision = "BLOCK_ACTION_OVERCLAIM"
    elif not contract.expected_behavior:
        decision = "HOLD_NEEDS_CONTRACT"
    elif patch.tests_passed and residuals:
        decision = "HOLD_TEST_HARNESS_ONLY_PASS"
    elif not patch.tests_passed:
        decision = "HOLD_CI_PASS_CONTRACT_GAP"
    else:
        decision = "PASS_CONTRACT_SCOPED"

    return ResidualLedger(
        ledger_id=_stable_id("qira-ledger", contract.contract_id, patch.patch_id, decision),
        contract_id=contract.contract_id,
        patch_id=patch.patch_id,
        residuals=residuals,
        missing_evidence=sorted(set(missing_evidence)),
        forbidden_change_findings=forbidden,
        unsupported_claim_findings=unsupported_claims,
        decision_token=decision,
    )


def build_action_license(patch: PatchCandidate, ledger: ResidualLedger) -> ActionLicense:
    token = ledger.decision_token
    if token.startswith("BLOCK"):
        return ActionLicense(
            license_id=_stable_id("qira-license", patch.patch_id, token),
            patch_id=patch.patch_id,
            patch_draft="BLOCK",
            pr_open="BLOCK",
            merge="BLOCK",
            deploy="BLOCK",
            public_claim="BLOCK",
            decision_reason=f"Blocked by {token}.",
        )
    if token == "PASS_CONTRACT_SCOPED":
        return ActionLicense(
            license_id=_stable_id("qira-license", patch.patch_id, token),
            patch_id=patch.patch_id,
            patch_draft="ALLOW",
            pr_open="ALLOW",
            merge="HOLD",
            deploy="BLOCK",
            public_claim="ALLOW_SCOPED_INTERNAL",
            decision_reason="Scoped local contract evidence supports draft/PR handling, while merge and deploy remain separately gated.",
        )
    return ActionLicense(
        license_id=_stable_id("qira-license", patch.patch_id, token),
        patch_id=patch.patch_id,
        patch_draft="ALLOW",
        pr_open="HOLD",
        merge="HOLD",
        deploy="BLOCK",
        public_claim="HOLD",
        decision_reason=f"Held by {token}; more evidence is needed before PR or release claims.",
    )


def build_patch_receipt(contract: BehaviorContract, patch: PatchCandidate) -> PatchReceipt:
    validator = build_validator_packet(contract)
    ledger = build_residual_ledger(contract, patch)
    license_card = build_action_license(patch, ledger)
    return PatchReceipt(
        receipt_id=_stable_id("qira-receipt", contract.contract_id, patch.patch_id, ledger.decision_token),
        contract=contract,
        patch=patch,
        validator=validator,
        residual_ledger=ledger,
        action_license=license_card,
    )


def build_release_gate_report(contract: BehaviorContract, patch: PatchCandidate) -> QiraReleaseGateReport:
    receipt = build_patch_receipt(contract, patch)
    ledger = receipt.residual_ledger
    summary = {
        "patch_id": patch.patch_id,
        "contract_id": contract.contract_id,
        "decision_token": ledger.decision_token,
        "residual_count": len(ledger.residuals),
        "missing_evidence_count": len(ledger.missing_evidence),
        "forbidden_change_count": len(ledger.forbidden_change_findings),
        "unsupported_claim_count": len(ledger.unsupported_claim_findings),
        "patch_draft": receipt.action_license.patch_draft,
        "pr_open": receipt.action_license.pr_open,
        "merge": receipt.action_license.merge,
        "deploy": receipt.action_license.deploy,
        "public_claim": receipt.action_license.public_claim,
    }
    return QiraReleaseGateReport(
        report_id=_stable_id("qira-report", patch.patch_id, ledger.decision_token),
        decision_token=ledger.decision_token,
        action_license=receipt.action_license,
        receipt=receipt,
        summary=summary,
        known_limits=[
            "Local or fixture evidence is not independent verification.",
            "A test pass does not imply merge, deploy, product, security, legal, or safety readiness.",
            "QIRA-1 does not execute arbitrary external tools or contact external services.",
        ],
    )


def sample_release_gate_report() -> QiraReleaseGateReport:
    contract = build_behavior_contract(
        "Add a read-only CLI demo for objective routing without network calls.",
        expected_behavior=[
            "CLI accepts a query and objective.",
            "CLI writes a local JSON receipt.",
            "CLI does not fetch network resources or request secrets.",
        ],
    )
    patch = PatchCandidate(
        patch_id=_stable_id("qira-patch", contract.contract_id, "sample"),
        contract_id=contract.contract_id,
        summary="Adds a local fixture-backed CLI demo and tests.",
        changed_files=["src/ai_objective_index/example_cli.py", "tests/test_example_cli.py"],
        tests_passed=True,
        test_summary="Fixture tests passed locally.",
        evidence_origin="local_fixture",
        requested_action="pr_open",
        declared_claims=["Scoped local fixture replay passed."],
    )
    return build_release_gate_report(contract, patch)
