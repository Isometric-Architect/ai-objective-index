# Manual Public Beta Launch Steps v0.2

This workspace prepares launch materials only. It does not publish, upload, submit, post, or contact external services.

1. Run `python -m pytest`.
2. Run `python -m ai_objective_index.smoke_all`.
3. Run `python -m ai_objective_index.final_preflight`.
4. Run `python -m ai_objective_index.realdata_claim_audit`.
5. Run `python -m ai_objective_index.manual_launch_packager`.
6. Review `GITHUB_RELEASE_DRAFT.md`.
7. Manually create a GitHub release if desired.
8. Manually create a Hugging Face Space if desired.
9. Manually create a Hugging Face Dataset if desired.
10. Manually post community feedback request if desired.

Keep the release read-only and claim-bounded.

## Private Deployment Links

- GitHub private staging repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- MCP Registry submission: HOLD, manual only.

These links are private deployment links unless the owner manually changes visibility. They are not a public release claim. `public_beta_mcp` records are source-traced registry metadata candidates; they are not verified, not safe/certified, not security certified, not a quality guarantee, and not purchasing advice.
