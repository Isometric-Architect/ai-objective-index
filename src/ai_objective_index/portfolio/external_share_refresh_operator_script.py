from __future__ import annotations

from pathlib import Path

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_refresh_manifest import SHARE_V2_DIR


OPERATOR_SCRIPT_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_OPERATOR_SCRIPT_V2.md"
SCREENSHOT_SCRIPT_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_SCREENSHOT_SCRIPT_V2.md"
VIDEO_SCRIPT_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_VIDEO_SCRIPT_V2.md"


def build_operator_script() -> str:
    return """# ResidualOps External-Safe Operator Script V2

1. Open `RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.html` locally.
2. Point to the claim ceiling banner first.
3. Say this is a static local refreshed demo and not a product launch.
4. Show AgentSec feedback second-run status: executed and incorporated.
5. Show QIRA, DataCapsule, and Portfolio status: skipped_missing_artifact.
6. Explain skipped candidates are HOLD, not failure and not success.
7. Show `external_action_count = 0`.
8. Show known limits and next actions.
9. Do not say product ready.
10. Do not say certified.
11. Do not promise live automation.
12. Do not show or describe private kernels, weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, or commercial routing policy.
"""


def build_screenshot_script() -> str:
    return """# ResidualOps External-Safe Screenshot Script V2

Capture only bounded screenshots where the claim ceiling banner is visible.

Suggested frames:

1. Claim ceiling banner and V2 title.
2. AgentSec executed/incorporated status.
3. QIRA, DataCapsule, and Portfolio skipped_missing_artifact rows.
4. `external_action_count = 0`.
5. Known limits.

Do not capture raw private data, credentials, tokens, local filesystem secrets, private kernels, or any screen that suggests certification, product readiness, or external action authorization.
"""


def build_video_script() -> str:
    return """# ResidualOps External-Safe Video Script V2

Narration:

This is a refreshed static local demo pack generated from the ROE-21 dashboard refresh. It shows one local AgentSec feedback second-run and three skipped/HOLD candidates that still need local artifacts or context. It is not an external pilot, not security certification, not code correctness proof, not legal/privacy/license/eval-clean proof, not product readiness, and not external action authorization.

Show:

1. Claim ceiling banner.
2. Static/no-network label.
3. AgentSec executed/incorporated row.
4. QIRA/DataCapsule/Portfolio skipped_missing_artifact rows.
5. `external_action_count = 0`.
6. Manifest and checksums.

Do not promise live connectors, production deployment, security certification, quality guarantee, or automated action execution.
"""


def write_refresh_operator_scripts() -> dict[str, str]:
    outputs = {
        str(OPERATOR_SCRIPT_V2_PATH).replace("\\", "/"): build_operator_script(),
        str(SCREENSHOT_SCRIPT_V2_PATH).replace("\\", "/"): build_screenshot_script(),
        str(VIDEO_SCRIPT_V2_PATH).replace("\\", "/"): build_video_script(),
    }
    for path_text, content in outputs.items():
        destination = _repo_root() / Path(path_text)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    return {path: "written" for path in outputs}
