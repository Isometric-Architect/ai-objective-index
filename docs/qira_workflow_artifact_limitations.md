# QIRA Workflow Artifact Limitations

QIRA workflow artifacts are review aids.

They are not:

- verification of a patch;
- security certification;
- quality guarantee;
- product-readiness proof;
- deployment approval;
- legal compliance proof;
- authorization for external actions.

The public template uses repository-owned CI evidence and committed task-packet metadata. Metadata can be incomplete, stale, or wrong. A HOLD/BLOCK result should be reviewed by the repository owner. A pass result means only that the public local checks did not detect the modeled blocking pattern under the supplied metadata and evidence.
