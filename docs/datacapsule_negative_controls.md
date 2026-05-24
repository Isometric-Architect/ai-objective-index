# DataCapsule Negative Controls

DataCapsule negative controls are local fixtures that should not pass as clean use-boundary evidence. They protect the public DataCapsule path from inflating weak metadata into unsupported claims.

Current local controls:

- Unsupported public claims such as privacy-compliant or eval-clean wording must block.
- Missing source records must hold for source and rights review.
- Prompt-injection risk flags must hold retrieval or summarization use.
- Action use must block because a DataCapsule cannot authorize external actions.

Negative controls do not prove that a corpus is safe, lawful, private, high quality, or evaluation-clean. They only check that known-bad local metadata fixtures are not accidentally treated as acceptable.

Run:

```bash
python -m ai_objective_index.datacapsule.corpus_manifest --run-sample
```

The generated negative-control result is written to:

`public_launch/datacapsule2/DATACAPSULE2_NEGATIVE_CONTROL_RESULT.json`
