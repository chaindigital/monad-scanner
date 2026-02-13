from __future__ import annotations

from scanner.signals.schema import SignalDraft


def clamp_int(x: float, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(round(x))))


def score_finding(kind: str, strength: float, base: int) -> int:
    # strength in [0..1], base around 40..70
    return clamp_int(base + 40 * strength, 0, 100)


def confidence_from_strength(strength: float) -> float:
    return max(0.05, min(0.99, 0.4 + 0.6 * strength))


def to_draft(category: str, kind: str, strength: float, explanation: str, evidence: dict, actions: list[str]) -> SignalDraft:
    base = {
        "ordering": 55,
        "conflict": 50,
        "hot_state": 45,
        "dependency": 50,
        "shift": 55,
    }.get(category, 50)

    return SignalDraft(
        category=category,  # type: ignore
        severity=score_finding(kind, strength, base),
        confidence=confidence_from_strength(strength),
        title=_title(category, kind),
        explanation=explanation,
        evidence=evidence,
        recommended_actions=actions,
    )


def _title(category: str, kind: str) -> str:
    if category == "ordering":
        return "Ordering sensitivity risk detected"
    if category == "conflict":
        return "Conflict / failure burst risk detected"
    if category == "hot_state":
        return "Hot state concentration detected"
    if category == "dependency":
        return "Hidden dependency clusters detected"
    return f"Risk signal: {kind}"
