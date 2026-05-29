from __future__ import annotations

from .datacapsule_manifest_summary import stable_id
from .datacapsule_pilot_receipt import (
    DataCapsuleCorpusManifest,
    DataCapsuleEvalLeakageSummary,
    DataCapsulePrivacyRiskSummary,
    DataCapsuleSourceRightsSummary,
    DataCapsuleUseBoundary,
    UseDecision,
)


def _decision_for_declared_use(use: str, manifest: DataCapsuleCorpusManifest) -> UseDecision:
    allowed = {item.lower() for item in manifest.declared_allowed_uses}
    blocked = {item.lower() for item in manifest.declared_disallowed_uses}
    if use in blocked:
        return "BLOCK"
    if use in allowed:
        return "ALLOW"
    return "HOLD"


def build_use_boundary(
    manifest: DataCapsuleCorpusManifest,
    rights: DataCapsuleSourceRightsSummary,
    privacy: DataCapsulePrivacyRiskSummary,
    eval_leakage: DataCapsuleEvalLeakageSummary,
) -> DataCapsuleUseBoundary:
    reasons: list[str] = []
    blocked: list[str] = []
    holds: list[str] = []
    train = _decision_for_declared_use("train", manifest)
    retrieve = _decision_for_declared_use("retrieve", manifest)
    evaluate = _decision_for_declared_use("evaluate", manifest)
    share = _decision_for_declared_use("share", manifest)
    commercial = _decision_for_declared_use("commercial", manifest)
    act: UseDecision = "BLOCK"

    if rights.rights_status.startswith("HOLD") or privacy.privacy_status.startswith("HOLD") or eval_leakage.leakage_status.startswith("HOLD"):
        if train == "ALLOW":
            train = "HOLD"
        if evaluate == "ALLOW" and eval_leakage.leakage_status.startswith("HOLD"):
            evaluate = "HOLD"
        if share == "ALLOW":
            share = "HOLD"
        if commercial == "ALLOW" and rights.commercial_use_declared is not True:
            commercial = "HOLD"
        reasons.append("Manifest has rights, privacy, or evaluation-boundary uncertainty.")
    if commercial == "ALLOW" and rights.commercial_use_declared is not True:
        commercial = "HOLD"
        reasons.append("Commercial use needs explicit license/terms evidence.")
    decisions = {
        "train": train,
        "retrieve": retrieve,
        "evaluate": evaluate,
        "share": share,
        "act": act,
        "commercial": commercial,
    }
    for use, decision in decisions.items():
        if decision == "BLOCK":
            blocked.append(use)
        elif decision == "HOLD":
            holds.append(use)
    if "act" in blocked:
        reasons.append("Action use defaults to BLOCK without separate action authorization.")
    return DataCapsuleUseBoundary(
        boundary_id=stable_id("datacapsule-boundary", manifest.manifest_id, decisions),
        manifest_id=manifest.manifest_id,
        train_use=train,
        retrieve_use=retrieve,
        evaluate_use=evaluate,
        share_use=share,
        act_use=act,
        commercial_use=commercial,
        reasons=reasons,
        blocked_uses=blocked,
        hold_uses=holds,
        next_actions=[
            "request license and terms evidence",
            "request privacy and consent evidence",
            "request train/eval split or overlap evidence",
            "keep action use blocked unless separately authorized",
        ],
    )
