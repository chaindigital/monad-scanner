from __future__ import annotations

import asyncio
import logging

log = logging.getLogger("scanner.pipeline.scheduler")


class Scheduler:
    def __init__(self, poll_interval_seconds: float, max_blocks_per_tick: int) -> None:
        self.poll_interval_seconds = poll_interval_seconds
        self.max_blocks_per_tick = max_blocks_per_tick
        self._stop = asyncio.Event()

    def stop(self) -> None:
        self._stop.set()

    async def loop(self, tick_fn):
        while not self._stop.is_set():
            try:
                await tick_fn(self.max_blocks_per_tick)
            except Exception as e:
                log.exception("scheduler tick failed err=%s", e)
            await asyncio.sleep(self.poll_interval_seconds)
