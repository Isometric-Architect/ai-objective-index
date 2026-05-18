from __future__ import annotations

import time
from collections.abc import Callable


class RateLimiter:
    def __init__(
        self,
        min_delay_seconds: float = 1.0,
        now_func: Callable[[], float] | None = None,
        sleep_func: Callable[[float], None] | None = None,
        disable_sleep: bool = False,
    ) -> None:
        self.min_delay_seconds = float(min_delay_seconds)
        self.now_func = now_func or time.time
        self.sleep_func = sleep_func or time.sleep
        self.disable_sleep = disable_sleep
        self._last_request_at: dict[str, float] = {}

    def record_request(self, domain: str) -> None:
        self._last_request_at[domain] = float(self.now_func())

    def next_allowed_time(self, domain: str) -> float:
        last = self._last_request_at.get(domain)
        if last is None:
            return float(self.now_func())
        return last + self.min_delay_seconds

    def wait_if_needed(self, domain: str) -> float:
        now = float(self.now_func())
        wait_seconds = max(0.0, self.next_allowed_time(domain) - now)
        if wait_seconds > 0 and not self.disable_sleep:
            self.sleep_func(wait_seconds)
        self.record_request(domain)
        return wait_seconds

