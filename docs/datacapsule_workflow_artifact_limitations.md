# DataCapsule Workflow Artifact Limitations

DataCapsule workflow artifacts are convenience outputs for repository-owned corpus manifests.

They are limited by the supplied metadata. Missing or stale manifest fields can produce HOLD decisions even when a corpus may be acceptable after separate review.

The workflow artifact does not:

- crawl directories;
- read private file contents;
- fetch URLs;
- call external services;
- call GitHub APIs by DataCapsule;
- post comments;
- handle tokens;
- prove legal sufficiency;
- prove privacy compliance;
- guarantee data quality;
- clear licenses;
- prove evaluation cleanliness;
- provide purchasing advice;
- authorize actions.

Use the artifact as a review aid, not as a legal, privacy, data-quality, procurement, or action decision.
