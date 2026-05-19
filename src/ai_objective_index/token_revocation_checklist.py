from __future__ import annotations

from pathlib import Path

from .public_launch_gate import OUTPUT_DIR


OUTPUT_PATH = OUTPUT_DIR / "TOKEN_REVOCATION_CHECKLIST.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def write_token_revocation_checklist() -> Path:
    text = """# Token Revocation Checklist

- Do not paste tokens into chat.
- Do not commit tokens.
- Do not store tokens in this repository.
- If no further Hugging Face upload is needed, revoke the temporary token.
- Go to Hugging Face Settings -> Access Tokens -> `aoi-private-upload` -> Delete/Revoke.
- If public visibility switch still needs HF API access, revoke after the switch.
- After revocation, the Hugging Face Space and Dataset remain uploaded.
"""
    return _write(OUTPUT_PATH, text)


def main() -> None:
    path = write_token_revocation_checklist()
    print(f"token_revocation_checklist: wrote={path}")


if __name__ == "__main__":
    main()
