# Feedback Reply Classification

The classifier is deterministic and local. It does not call external LLMs or APIs.

Accepted classifications create local feedback memory candidates or local second-run candidates. HOLD decisions request more context, consent, or redaction review. BLOCK decisions stop external-action requests, certification/readiness requests, secret/private-data findings, and private-kernel disclosures.

Classification does not authorize external action or certify any result.
