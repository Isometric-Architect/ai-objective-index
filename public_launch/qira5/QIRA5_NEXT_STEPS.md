# QIRA-5 Next Steps

1. Wire this local packet generator into the existing reusable GitHub Action wrapper.
2. Let CI provide changed-file lists or diff artifacts explicitly instead of letting QIRA call GitHub APIs.
3. Add project-owned evidence fields for test results after commands are executed by the repository's normal CI.
4. Keep merge, deploy, package upload, registry submission, and public readiness claims behind separate gates.

QIRA-5 generates conservative local task packets. It does not call GitHub APIs, run git commands, apply patches, execute tests, deploy, upload, publish, handle tokens, or certify code quality/security.
