from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .real_pypi_upload_gate import _repo_root


TEMPLATE_PATH = Path("private_templates") / "PRIVATE_KERNEL_INVENTORY_TEMPLATE.md"
NOTE_PATH = Path("public_launch") / "wave12_tech_protection" / "PRIVATE_KERNEL_TEMPLATE_NOTE.md"
GITIGNORE_ENTRIES = [
    ".aoi_private/",
    "private_kernel/",
    "private_kernels/",
    "private_data/",
    "private_calibration/",
    "private_negative_controls/",
    "private_provider_priors/",
    "*.pypirc",
    ".pypirc",
]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _template_text() -> str:
    return """# Private Kernel Inventory Template

This placeholder-only template is safe to commit. Do not place real private values in this file.

## Private Ranking Weights

- Placeholder: `<describe private weight family without values>`

## Threshold Policy

- Placeholder: `<describe threshold category without numbers>`

## Anti-Gaming Rules

- Placeholder: `<describe rule family without trigger details>`

## Provider Trust Priors

- Placeholder: `<describe prior source class without provider-specific values>`

## Private Negative-Control Bank

- Placeholder: `<list control category names only>`

## Private Probe Seeds

- Placeholder: `<list probe family names only>`

## Receipt Weighting

- Placeholder: `<describe weighting inputs without formula or coefficients>`

## Commercial Routing Policy

- Placeholder: `<describe policy category without customer/provider details>`

## Enterprise Data Policy

- Placeholder: `<describe data-governance bucket without sensitive datasets>`

## Freshness Strategy

- Placeholder: `<describe refresh tier without target list or cadence values>`
"""


def ensure_private_gitignore_entries() -> list[str]:
    path = _repo_root() / ".gitignore"
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    added: list[str] = []
    lines = text.splitlines()
    for entry in GITIGNORE_ENTRIES:
        if entry not in lines:
            lines.append(entry)
            added.append(entry)
    if added:
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return added


def template_contains_only_placeholders(text: str) -> bool:
    lower = text.lower()
    blocked = ["ghp_", "github_pat_", "pypi-", "hf_", " = 0.", ": 0.", "provider trust prior:"]
    return "placeholder" in lower and not any(marker in lower for marker in blocked)


def run_private_kernel_template_generator(write_files: bool = True) -> dict[str, object]:
    template = _template_text()
    added_entries = ensure_private_gitignore_entries() if write_files else []
    if write_files:
        _write(TEMPLATE_PATH, template)
        _write(
            NOTE_PATH,
            f"""# Private Kernel Template Note

Generated at: {datetime.now(UTC).isoformat()}

`private_templates/PRIVATE_KERNEL_INVENTORY_TEMPLATE.md` is placeholder-only and safe to commit.

Do not commit real private ranking weights, thresholds, anti-gaming rules, provider trust priors, private negative-control seeds, private probe seeds, private receipt weighting, commercial routing policy, enterprise data strategy, or freshness strategy.

Private operational inventories should live under ignored paths such as `.aoi_private/`, `private_kernel/`, or `private_calibration/`.
""",
        )
    return {
        "template_path": str(TEMPLATE_PATH),
        "note_path": str(NOTE_PATH),
        "placeholder_only": template_contains_only_placeholders(template),
        "gitignore_entries": GITIGNORE_ENTRIES,
        "gitignore_entries_added": added_entries,
        "token_printed": False,
        "mcp_registry_submission_performed": False,
    }


def main() -> None:
    result = run_private_kernel_template_generator()
    print(f"private_kernel_template_generator: placeholder_only={result['placeholder_only']}")


if __name__ == "__main__":
    main()
