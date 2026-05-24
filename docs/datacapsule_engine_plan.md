# DataCapsule / AIDREG Engine Plan

DataCapsule is the data-governance vertical for AI-facing data objects. It should decide whether data can be used for retrieval, training, evaluation, memory, summarization, sharing, or action contexts under explicit source, rights, risk, and claim-ceiling boundaries.

First MVP:

- local corpus metadata intake
- source and license field checks
- use-right split for train, retrieve, evaluate, summarize, share, and act
- privacy, poison, prompt-injection, stale-data, and eval-leak flags
- DataCapsule report
- ALLOW/HOLD/BLOCK decision for each use class

DataCapsule should be third because the opportunity is large but the data-policy surface is wider than QIRA and AgentSec. The MVP should begin with local metadata and user-supplied source records, not live crawling.

DataCapsule must not claim legal sufficiency, privacy compliance, quality guarantee, or purchasing advice. It can surface evidence gaps, residual risks, and allowed/held/blocked use boundaries.
