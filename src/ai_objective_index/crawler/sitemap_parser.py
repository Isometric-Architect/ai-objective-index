from __future__ import annotations

import xml.etree.ElementTree as ET


def parse_sitemap_xml(text: str) -> list[str]:
    root = ET.fromstring(text)
    urls: list[str] = []
    for element in root.iter():
        if element.tag.endswith("loc") and element.text:
            urls.append(element.text.strip())
    return urls


def filter_seed_urls(
    urls: list[str],
    include_keywords: list[str] | None = None,
    exclude_keywords: list[str] | None = None,
) -> list[str]:
    include = [item.lower() for item in include_keywords or []]
    exclude = [item.lower() for item in exclude_keywords or []]
    filtered: list[str] = []
    for url in urls:
        lowered = url.lower()
        if include and not any(keyword in lowered for keyword in include):
            continue
        if exclude and any(keyword in lowered for keyword in exclude):
            continue
        filtered.append(url)
    return filtered

