from __future__ import annotations

import logging
from typing import Any

import httpx
import orjson

from scanner.utils.backoff import jitter_sleep

log = logging.getLogger("scanner.rpc.jsonrpc")


class JsonRpcClient:
    def __init__(self, url: str, timeout: float = 10.0, max_retries: int = 5) -> None:
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries

    async def call(self, method: str, params: list[Any] | None = None) -> Any:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
        attempt = 0
        last_err: Exception | None = None

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while attempt <= self.max_retries:
                try:
                    r = await client.post(
                        self.url,
                        content=orjson.dumps(payload),
                        headers={"content-type": "application/json"},
                    )
                    r.raise_for_status()
                    data = r.json()
                    if "error" in data:
                        raise RuntimeError(f"RPC error: {data['error']}")
                    return data["result"]
                except Exception as e:  # small surface, logged; backoff occurs
                    last_err = e
                    log.warning("RPC call failed method=%s attempt=%s err=%s", method, attempt, e)
                    jitter_sleep(base=0.2, factor=1.8, attempt=attempt, max_sleep=5.0)
                    attempt += 1

        raise RuntimeError(f"RPC call failed after retries: {method}") from last_err
