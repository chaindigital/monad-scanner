from __future__ import annotations

import random
import time


def jitter_sleep(base: float, factor: float, attempt: int, max_sleep: float = 10.0) -> None:
    # Small and predictable backoff with jitter to avoid thundering herds.
    sleep = min(max_sleep, base * (factor**attempt))
    sleep = sleep * (0.7 + 0.6 * random.random())
    time.sleep(sleep)
