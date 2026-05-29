from ai_objective_index.portfolio.datacapsule_eval_leakage import build_eval_leakage_summary
from ai_objective_index.portfolio.datacapsule_manifest_summary import SAMPLE_MANIFEST, build_corpus_manifest
from ai_objective_index.portfolio.datacapsule_privacy_risk import build_privacy_risk_summary
from ai_objective_index.portfolio.datacapsule_source_rights import build_source_rights_summary
from ai_objective_index.portfolio.datacapsule_use_boundary import build_use_boundary


def test_datacapsule_act_use_defaults_block():
    manifest = build_corpus_manifest(SAMPLE_MANIFEST)
    boundary = build_use_boundary(manifest, build_source_rights_summary(manifest), build_privacy_risk_summary(manifest), build_eval_leakage_summary(manifest))

    assert boundary.act_use == "BLOCK"
    assert "act" in boundary.blocked_uses


def test_datacapsule_train_use_holds_when_unknown():
    payload = dict(SAMPLE_MANIFEST)
    payload["declared_allowed_uses"] = ["train"]
    manifest = build_corpus_manifest(payload)
    boundary = build_use_boundary(manifest, build_source_rights_summary(manifest), build_privacy_risk_summary(manifest), build_eval_leakage_summary(manifest))

    assert boundary.train_use == "HOLD"
