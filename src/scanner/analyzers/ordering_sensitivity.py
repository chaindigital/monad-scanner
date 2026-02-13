from __future__ import annotations

from typing import Any

from scanner.analyzers.base import AnalyzerContext

# Heuristic module: designed to be upgraded as richer traces become available.


class OrderingSensitivityAnalyzer:
    name = "ordering_sensitivity"

    async def analyze(self, ctx: AnalyzerContext) -> list[dict[str, Any]]:
        # Minimal heuristic: repeated status flips across adjacent txs with shared "to" addresses.
        # If receipts include status + to, we detect adjacency correlations.
        txs = ctx.tx_hashes
        if not txs:
            return []

        pairs: list[tuple[str, str]] = []
        for i in range(len(txs) - 1):
            a, b = txs[i], txs[i + 1]
            ra = ctx.receipts.get(a) or {}
            rb = ctx.receipts.get(b) or {}
            ta = (ra.get("to") or "").lower()
            tb = (rb.get("to") or "").lower()
            sa = ra.get("status")
            sb = rb.get("status")
            if ta and tb and ta == tb and sa is not None and sb is not None and sa != sb:
                pairs.append((a, b))

        if not pairs:
            return []

        return [
            {
                "kind": "ordering_cluster",
                "pairs": pairs[:25],
                "reason": "Adjacent txs to same target show divergent statuses (order-sensitive hint).",
                "strength": min(1.0, 0.2 + 0.03 * len(pairs)),
            }
        ]
