# DataCapsule Workflow Opt-In Runbook

This runbook explains how a repository owner can enable the DataCapsule optional workflow artifact template.

## Steps

1. Review `examples/datacapsule7_repository_manifest_workflow.yml`.
2. Confirm the repository already has a committed corpus manifest in CSV, JSONL, or JSON format.
3. Copy the example into `.github/workflows/` only in the target repository.
4. Run the workflow manually with `workflow_dispatch`.
5. Download the workflow artifact and review HOLD/BLOCK items before using the corpus.

## Required Review

DataCapsule artifacts are local metadata review outputs. They do not replace rights, privacy, license, data-quality, benchmark-contamination, security, product, procurement, or legal review.

## Safety Notes

- Do not add credentials to the manifest.
- Do not commit `.env`, `.pypirc`, private datasets, or private kernel inventories.
- Keep exact private thresholds, receipt weighting, private negative controls, private probe seeds, and commercial data strategy outside public artifacts.
- The workflow should remain manual until a separate package explicitly adds a safer automatic trigger.
