from __future__ import annotations

from fnmatch import fnmatch
from urllib.parse import urlparse


RobotsRules = dict[str, list[str]]


def parse_robots_txt(text: str) -> RobotsRules:
    """Parse a small subset of robots.txt User-agent/Disallow rules."""

    rules: RobotsRules = {}
    active_agents: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue

        key, value = [part.strip() for part in line.split(":", 1)]
        key = key.lower()

        if key == "user-agent":
            agent = value.lower() or "*"
            active_agents = [agent]
            rules.setdefault(agent, [])
        elif key == "disallow" and active_agents:
            for agent in active_agents:
                rules.setdefault(agent, []).append(value)

    return rules


def _matching_rules(user_agent: str, rules: RobotsRules) -> list[str]:
    agent = user_agent.lower()
    matches: list[str] = []

    for candidate, disallows in rules.items():
        if candidate == "*" or candidate in agent:
            matches.extend(disallows)

    return matches


def is_allowed(url: str, user_agent: str, robots_txt: str | None) -> bool:
    """Return whether the URL is allowed by the provided robots text.

    Missing robots text is conservative: callers must explicitly provide rules
    before a URL is considered allowed.
    """

    if robots_txt is None:
        return False

    rules = parse_robots_txt(robots_txt)
    path = urlparse(url).path or "/"

    for pattern in _matching_rules(user_agent, rules):
        if pattern == "":
            continue
        if "*" in pattern:
            if fnmatch(path, pattern):
                return False
        elif path.startswith(pattern):
            return False

    return True

