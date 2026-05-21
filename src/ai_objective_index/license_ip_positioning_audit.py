from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "wave12_tech_protection" / "LICENSE_IP_POSITIONING_AUDIT.json"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def detect_license_type(text: str) -> str:
    lower = text.lower()
    if "mit license" in lower and "permission is hereby granted" in lower:
        return "MIT"
    if "apache license" in lower:
        return "Apache"
    if "gnu general public license" in lower:
        return "GPL"
    return "UNKNOWN"


def run_license_ip_positioning_audit(write_result: bool = True) -> dict[str, Any]:
    license_path = _repo_root() / "LICENSE"
    readme_path = _repo_root() / "README.md"
    license_text = license_path.read_text(encoding="utf-8", errors="ignore") if license_path.exists() else ""
    readme_text = readme_path.read_text(encoding="utf-8", errors="ignore") if readme_path.exists() else ""
    license_type = detect_license_type(license_text)
    readme_references_license = "license" in readme_text.lower()
    warnings: list[str] = []
    errors: list[str] = []

    if not license_path.exists():
        decision = "BLOCK_LICENSE_MISSING_FOR_PUBLIC_REPO"
        errors.append("LICENSE file is missing.")
    elif license_type == "MIT":
        decision = "PASS_LICENSE_PRESENT"
        warnings.append("MIT is permissive; copying/forking may be allowed under its terms.")
    else:
        decision = "HOLD_LICENSE_REVIEW_RECOMMENDED"
        warnings.append("License exists but type should be reviewed before increasing distribution.")
    if not readme_references_license:
        warnings.append("README does not visibly reference license terms.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "license_exists": license_path.exists(),
        "license_type": license_type,
        "readme_references_license": readme_references_license,
        "non_legal_note": "This is operational positioning, not legal advice. Consult a legal professional for IP, patent, trademark, or licensing strategy.",
        "future_options": ["keep open source for adoption", "dual-license later", "keep core open and commercial/private kernel closed", "consult legal professional for IP/patent/trademark strategy"],
        "mcp_registry_submission_performed": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_license_ip_positioning_audit()
    print(f"license_ip_positioning_audit: {result['decision']} license={result['license_type']}")


if __name__ == "__main__":
    main()
