from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AnalyzerContext:
    chain_id: str
    block_number: int
    block_hash: str
    tx_hashes: list[str]
    receipts: dict[str, dict[str, Any] | None]  # tx_hash -> receipt (optional)
    raw_block: dict[str, Any]


class Analyzer(Protocol):
    name: str

    async def analyze(self, ctx: AnalyzerContext) -> list[dict[str, Any]]:
        """
        Returns raw findings (not final Signals yet).
        Each finding is a dict with enough data to be scored and explained.
        """
        ...
