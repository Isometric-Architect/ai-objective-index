from __future__ import annotations

from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .robots_policy import is_allowed


def fetch_url(
    url: str,
    user_agent: str = "AI-Objective-Index-Bot/0.1",
    allow_network: bool = False,
    robots_txt: str | None = None,
    cache: Any | None = None,
) -> dict[str, Any]:
    """Fetch a URL only when explicitly enabled by the caller."""

    if not allow_network:
        raise RuntimeError("Live network fetch disabled. Use fixtures or pass allow_network=True.")

    if not is_allowed(url, user_agent=user_agent, robots_txt=robots_txt):
        raise PermissionError(f"Robots policy does not allow fetching {url}.")

    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=20) as response:  # noqa: S310 - explicit opt-in fetcher.
        body = response.read()
        content_type = response.headers.get("content-type", "text/html")
        encoding = response.headers.get_content_charset() or "utf-8"
        content = body.decode(encoding, errors="replace")

    record = {
        "url": url,
        "domain": urlparse(url).netloc,
        "content_type": content_type,
        "content": content,
    }
    if cache is not None:
        record["cache"] = cache.write_source(url, content, content_type=content_type)
    return record

