from __future__ import annotations

from .qira_patch_classifier import stable_id
from .qira_pilot_receipt import QIRACIEvidenceSummary


def build_ci_evidence_summary(
    task_id: str,
    source_type: str = "generated_sample",
    tests_passed: bool | None = True,
    lint_passed: bool | None = None,
    typecheck_passed: bool | None = None,
    build_passed: bool | None = None,
) -> QIRACIEvidenceSummary:
    missing: list[str] = []
    warnings: list[str] = []
    if tests_passed is None:
        missing.append("test_result")
    if lint_passed is None:
        missing.append("lint_result")
    if typecheck_passed is None:
        missing.append("typecheck_result")
    if build_passed is None:
        missing.append("build_result")
    if source_type == "generated_sample":
        missing.append("independent_ci_run")
        warnings.append("Generated sample evidence is useful for packaging shape only.")
    if tests_passed is False:
        status = "PARTIAL_CI_EVIDENCE"
        warnings.append("Tests were reported as failing.")
    elif source_type == "local_fixture" and not missing:
        status = "LOCAL_FIXTURE_EVIDENCE"
    elif not tests_passed and not any(value is True for value in [lint_passed, typecheck_passed, build_passed]):
        status = "NO_CI_EVIDENCE"
    else:
        status = "PARTIAL_CI_EVIDENCE"
    return QIRACIEvidenceSummary(
        ci_evidence_id=stable_id("qira-ci-summary", task_id, source_type, tests_passed, lint_passed, typecheck_passed, build_passed),
        task_id=task_id,
        source_type=source_type,  # type: ignore[arg-type]
        tests_passed=tests_passed,
        tests_failed=0 if tests_passed else None,
        lint_passed=lint_passed,
        typecheck_passed=typecheck_passed,
        build_passed=build_passed,
        coverage_reported=False,
        evidence_status=status,  # type: ignore[arg-type]
        missing_evidence=sorted(set(missing)),
        warnings=warnings,
    )
