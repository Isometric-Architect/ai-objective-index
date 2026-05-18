from __future__ import annotations

from urllib.parse import urlparse


def normalize_github_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return url.strip().rstrip("/")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return f"https://github.com/{'/'.join(parts)}".rstrip("/")
    owner, repo = parts[0], parts[1].removesuffix(".git")
    return f"https://github.com/{owner}/{repo}"


def github_repo_to_readme_url(repo_url: str) -> str | None:
    normalized = normalize_github_url(repo_url)
    parsed = urlparse(normalized)
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    return f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md"

