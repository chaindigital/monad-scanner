from __future__ import annotations

from collections import Counter

from scanner.analyzers.base import AnalyzerContext


class HotStateAnalyzer:
    name = "hot_state"

    async def analyze(self, ctx: AnalyzerContext) -> list[dict]:
        # Approximate hot zones from log topics (if present) and target addresses.
        # This is intentionally heuristic: it produces "hot candidates" that can be enriched later.
        c = Counter()

        for h in ctx.tx_hashes:
            r = ctx.receipts.get(h) or {}
            to = (r.get("to") or "").lower()
            if to:
                c[f"to:{to}"] += 1

            logs = r.get("logs") or []
            for lg in logs[:50]:
                topics = lg.get("topics") or []
                if topics:
                    c[f"topic:{topics[0].lower()}"] += 1

        if not c:
            return []

        top = c.most_common(5)
        if top[0][1] < 5:
            return []  # avoid noise on tiny blocks

        return [
            {
                "kind": "hot_candidates",
                "top": top,
                "reason": "Repeated touches to same targets/topics suggest concentrated state pressure.",
                "strength": min(1.0, 0.15 + 0.05 * top[0][1]),
            }
        ]
