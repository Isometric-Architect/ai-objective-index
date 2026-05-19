# Private Reviewer Workflow

Private review is the safer path before public launch.

1. Run `python -m ai_objective_index.public_launch_gate`.
2. Run `python -m ai_objective_index.private_reviewer_packager`.
3. Share private GitHub/Hugging Face links only with trusted reviewers.
4. Ask reviewers to test:
   - wrong fields
   - bad rankings
   - missing source traces
   - confusing claim boundaries
5. Keep links private unless the owner manually decides to switch public.

Reviewer language must stay careful: AOI is read-only and the registry candidates are not verified, not security certified, not a quality guarantee, and not purchasing advice.
