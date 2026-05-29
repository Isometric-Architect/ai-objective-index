# ROE-10 First DataCapsule Pilot Receipt Packager

ROE-10 packages a local/offline DataCapsule manifest review into a reviewer-facing pilot receipt bundle.

It shows the shape:

CorpusManifest -> Source/Rights Summary -> Privacy/PII Risk Summary -> Evaluation Boundary -> Use Boundary -> DataCapsule Receipt -> Reviewer Readout -> Feedback Memory.

ROE-10 reviews manifest metadata only. It does not crawl, fetch URLs, inspect raw private content, upload data, train models, call external APIs, call GitHub APIs, request tokens, or make legal/privacy/license/evaluation-quality claims.

Commands:

```bash
python -m ai_objective_index.portfolio.datacapsule_pilot_packager --sample
python -m ai_objective_index.portfolio.roe10_datacapsule_pilot_gate
```
