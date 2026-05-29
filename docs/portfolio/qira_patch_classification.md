# QIRA Patch Classification

Patch classification summarizes changed-file categories and risk flags.

Public-safe risk flags include:

- auth or token handling
- network behavior
- subprocess or shell surface
- filesystem write
- dependency change
- release config change
- permission scope change
- generated code
- large diff

Classification can ALLOW review, HOLD for evidence or owner/security review, or BLOCK secret/external-action risk. It is not a guarantee of correctness or quality.
