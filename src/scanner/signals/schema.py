from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Category = Literal["ordering", "conflict", "hot_state", "dependency", "shift"]


@dataclass(frozen=True)
class SignalDraft:
    category: Category
    severity: int
    confidence: float
    title: str
    explanation: str
    evidence: dict[str, Any] | None
    recommended_actions: list[str] | None
