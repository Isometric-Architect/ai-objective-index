# DataCapsule Negative Controls

DataCapsule negative controls are local fixtures that should not pass as clean use-boundary evidence. They protect the public DataCapsule path from inflating weak metadata into unsupported claims.

Current local controls:

- Unsupported public claims such as privacy-compliant or eval-clean wording must block.
- Missing source records must hold for source and rights review.
- Prompt-injection risk flags must hold retrieval or summarization use.
- Action use must block because a DataCapsule cannot authorize external actions.

Negative controls do not prove that a corpus is safe, lawful, private, high quality, or evaluation-clean. They only check that known-bad local metadata fixtures are not accidentally treated as acceptable.

DataCapsule-5 adds a fuller public-safe fixture corpus for repeated regression checks across use-rights, privacy, prompt-injection, eval-leak, unsupported-claim, missing-source, and action-boundary cases.

Run the newer package:

```bash
python -m ai_objective_index.datacapsule.package5
```

The DataCapsule-5 negative-control result is written to:

`public_launch/datacapsule5/DATACAPSULE5_NEGATIVE_CONTROL_RESULT.json`
