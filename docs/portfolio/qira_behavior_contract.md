# QIRA Behavior Contract

The behavior contract states what a patch is expected to do, what it is not meant to do, forbidden behavior, required evidence, and negative-control expectations.

ROE-9 contracts include:

- expected behavior clauses
- non-goals
- forbidden merge/deploy/publish/comment/external-mutation behavior
- required evidence such as tests, docs, no secret diff, and reviewer acknowledgement
- negative controls for secrets, deploy scripts, auth scope changes, and missing test evidence

The contract is a review boundary, not proof that implementation is correct.
