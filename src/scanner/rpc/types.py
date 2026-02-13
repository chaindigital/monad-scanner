from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class BlockRef:
    number: int
    hash: str
    parent_hash: str | None
    timestamp: datetime | None
    tx_hashes: list[str]
    raw: dict[str, Any]
