# Residual Commit Plan

Do not commit all residual files at once. Candidate files should be grouped into future scoped packages.

## Candidate For Future Commit

- `CHANGELOG.md`
- `README.md`
- `docs/community_launch.md`
- `docs/huggingface_demo.md`
- `docs/launch_notes.md`
- `docs/post_public_observation.md`
- `docs/public_metrics_baseline.md`
- `docs/worktree_hygiene_policy.md`
- `public_launch/AI_REVIEWER_SIMULATION_RESULT.json`
- `public_launch/FINAL_PUBLIC_DRY_RUN_RESULT.json`
- `public_launch/NO_CONTACT_LAUNCH_GATE_RESULT.json`
- `public_launch/POST_PUBLIC_STABILIZATION_RESULT.json`
- `public_launch/PREPUBLIC_STATE_REPORT.json`
- `public_launch/PREPUBLIC_SYNC_RESULT.json`
- `public_launch/PUBLIC_BETA_MESSAGE_GUARD_RESULT.json`
- `public_launch/PUBLIC_ISSUE_LOOP_RESULT.json`
- `public_launch/PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json`
- `public_launch/PUBLIC_URL_QA_RESULT.json`
- `public_launch/PUBLIC_VISIBILITY_SWITCH_DRY_RUN.json`
- `public_launch/PUBLIC_VISIBILITY_SWITCH_RESULT.json`
- `docs/package_8n_public_observation_runner.md`
- `docs/public_observation_runner.md`
- `docs/residual_worktree_review_policy.md`
- `public_ops/HF_PARQUET_CONVERTER_NOTIFICATION.md`
- `public_ops/HF_PARQUET_CONVERTER_NOTIFICATION_v0_1.json`
- `public_ops/observation/`
- `public_ops/residual_review/`
- `src/ai_objective_index/github_link_binder.py`
- `src/ai_objective_index/github_post_upload_qa.py`
- `src/ai_objective_index/observation_decision_gate.py`
- `src/ai_objective_index/public_metrics_snapshot.py`
- `src/ai_objective_index/public_observation_runner.py`
- `src/ai_objective_index/public_switch_preflight.py`
- `src/ai_objective_index/residual_worktree_review.py`
- `tests/test_github_link_binder.py`
- `tests/test_github_post_upload_qa.py`
- `tests/test_github_upload_assets.py`
- `tests/test_hf_upload_assets.py`
- `tests/test_hf_upload_audit.py`
- `tests/test_hf_upload_packager.py`
- `tests/test_observation_decision_gate.py`
- `tests/test_package_8n_assets.py`
- `tests/test_public_metrics_snapshot.py`
- `tests/test_public_observation_runner.py`
- `tests/test_public_switch_preflight.py`
- `tests/test_residual_worktree_review.py`

## Current Recommendation

Observe public deployment first; defer residual cleanup to a scoped cleanup package.
