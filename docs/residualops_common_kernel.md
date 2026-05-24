# ResidualOps Common Kernel

ResidualOps is the shared operating language behind the current QIRA, AgentSec, and DataCapsule prototypes.

Public-safe concepts:

- **Packet / Manifest / Capsule:** a bounded input object supplied by the repository or user.
- **Check / Probe / Review:** deterministic local analysis over supplied metadata or fixtures.
- **Receipt / Result / Report:** a local artifact that records what was checked and which evidence is missing.
- **ALLOW / HOLD / BLOCK:** conservative route labels.
- **Artifact Bridge:** an opt-in wrapper that turns repository-owned metadata into local review artifacts.
- **Claim Boundary:** a visible limit on what the artifact may and may not claim.

Private kernel details remain private:

- exact ranking-weight values
- exact threshold policy
- anti-gaming rules
- provider trust priors
- private negative-control banks
- private probe seeds
- commercial routing policy
- enterprise data policy

The public kernel is intentionally useful to AI agents and developers without exposing private calibration or commercial operating policy. ALLOW/HOLD/BLOCK labels are routing aids, not verification, security certification, quality guarantees, product-readiness proof, legal advice, purchasing advice, or action authorization.
