from __future__ import annotations

from pathlib import Path

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_pack_manifest import SHARE_DIR


OPERATOR_SCRIPT_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_OPERATOR_SCRIPT.md"
SCREENSHOT_SCRIPT_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_SCREENSHOT_SCRIPT.md"
VIDEO_SCRIPT_PATH = SHARE_DIR / "RESIDUALOPS_EXTERNAL_SAFE_VIDEO_SCRIPT.md"


def build_operator_script() -> str:
    return """# ResidualOps External-Safe Operator Script

1. Open `RESIDUALOPS_EXTERNAL_SAFE_DEMO.html` locally.
2. Start by pointing to the claim ceiling banner.
3. Say this is a static local demo and not a product launch.
4. Show the three vertical cards: AgentSec, QIRA, and DataCapsule.
5. Show the ALLOW/HOLD/BLOCK matrix.
6. Show the second-run status and feedback memory.
7. Show known limits and next actions.
8. Do not say product ready.
9. Do not say certified.
10. Do not promise live automation.
11. Do not show or describe private kernels, weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, or commercial routing policy.
"""


def build_screenshot_script() -> str:
    return """# ResidualOps External-Safe Screenshot Script

Capture only bounded screenshots where the claim ceiling banner is visible.

Suggested frames:

1. Claim ceiling banner and dashboard title.
2. Three vertical cards.
3. ALLOW/HOLD/BLOCK and second-run summary.
4. Known limits.

Do not capture raw private data, credentials, tokens, local filesystem secrets, private kernels, or any screen that suggests certification, product readiness, or external action authorization.
"""


def build_video_script() -> str:
    return """# ResidualOps External-Safe Video Script

Narration:

This is a static local demo pack for bounded architecture review. It summarizes local receipt artifacts for AgentSec, QIRA, and DataCapsule. It is not an external pilot, not security certification, not code correctness proof, not legal/privacy/license/eval-clean proof, not product readiness, and not external action authorization.

Show:

1. Claim ceiling banner.
2. Static/no-network label.
3. Vertical cards.
4. ALLOW/HOLD/BLOCK matrix.
5. Feedback and second-run status.
6. Manifest and checksums.

Do not promise live connectors, production deployment, security certification, quality guarantee, or automated action execution.
"""


def write_operator_scripts() -> dict[str, str]:
    outputs = {
        str(OPERATOR_SCRIPT_PATH).replace("\\", "/"): build_operator_script(),
        str(SCREENSHOT_SCRIPT_PATH).replace("\\", "/"): build_screenshot_script(),
        str(VIDEO_SCRIPT_PATH).replace("\\", "/"): build_video_script(),
    }
    for path_text, content in outputs.items():
        destination = _repo_root() / Path(path_text)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    return {path: "written" for path in outputs}
