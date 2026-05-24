# QIRA-3 Patch Classification

QIRA-3 adds local patch path classification on top of QIRA-2 packet intake.

It classifies changed files into conservative categories:

- source
- test
- docs
- config
- CI
- dependency
- data or generated artifact
- private or secret
- path escape
- unknown

The classifier can add warnings or blocks for path escape, private marker, credential marker, dependency, CI, config, generated artifact, or unknown paths. It does not apply patches, run commands, fetch network resources, or decide merge/deploy readiness.

Path classification is a release-gate input. It is not proof that a patch is correct, safe, secure, production ready, or legally sufficient.
