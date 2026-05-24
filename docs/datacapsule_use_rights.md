# DataCapsule Use Rights

DataCapsule separates AI-facing data use into six classes:

- `train`
- `retrieve`
- `evaluate`
- `summarize`
- `share`
- `act`

Each use class receives one conservative decision:

- `ALLOW_USE`
- `HOLD_SOURCE_RIGHTS_REVIEW`
- `HOLD_PRIVACY_REVIEW`
- `HOLD_EVAL_LEAK_REVIEW`
- `HOLD_PROMPT_INJECTION_REVIEW`
- `HOLD_STALENESS_REVIEW`
- `BLOCK_ACTION_USE`
- `BLOCK_LICENSE_RESTRICTED`
- `BLOCK_PRIVACY_RISK`
- `BLOCK_UNSUPPORTED_CLAIM`

The public MVP treats action use as blocked by default because data metadata is not action permission. Broad use classes such as training and sharing require clearer source, license, and privacy evidence than local retrieval or summarization. DataCapsule-2 can also hold retrieval or summarization when a repository-supplied manifest marks prompt-injection risk.

These decisions are review boundaries. They are not legal advice, privacy compliance, license clearance, product readiness, purchasing advice, or action authorization.
