# QIRA-7 Next Steps

1. Keep the workflow example in `examples/` until the repository owner opts in.
2. In an enabled repository, run tests with normal CI steps before invoking the bridge.
3. Pass the recorded status and exit code to QIRA-7 as metadata.
4. Publish QIRA artifacts as workflow artifacts only if the repository owner wants them.

QIRA-7 does not run project commands, call GitHub APIs, apply patches, merge, deploy, upload packages, publish registry metadata, or handle tokens.
