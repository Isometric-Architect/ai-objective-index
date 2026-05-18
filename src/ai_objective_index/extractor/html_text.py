from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urljoin


class _AOIHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text_parts: list[str] = []
        self.title_parts: list[str] = []
        self.links: list[str] = []
        self._in_title = False
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self._ignored_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "a":
            for key, value in attrs:
                if key.lower() == "href" and value:
                    self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        stripped = " ".join(data.split())
        if not stripped:
            return
        if self._in_title:
            self.title_parts.append(stripped)
        self.text_parts.append(stripped)


def _parse(html: str) -> _AOIHTMLParser:
    parser = _AOIHTMLParser()
    parser.feed(html)
    return parser


def strip_html(html: str) -> str:
    parser = _parse(html)
    return " ".join(parser.text_parts)


def extract_title(html: str) -> str | None:
    parser = _parse(html)
    title = " ".join(parser.title_parts).strip()
    return title or None


def extract_links(html: str, base_url: str | None = None) -> list[str]:
    parser = _parse(html)
    links = parser.links
    if base_url:
        return [urljoin(base_url, link) for link in links]
    return links

