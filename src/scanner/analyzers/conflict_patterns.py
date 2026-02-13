from __future__ import annotations

from scanner.analyzers.base import AnalyzerContext


class ConflictPatternsAnalyzer:
    name = "conflict_patterns"

    async def analyze(self, ctx: AnalyzerContext) -> list[dict]:
        # Simple: bursts of failures/reverts in the same block.
        failures = 0
        samples = []
        for h in ctx.tx_hashes:
            r = ctx.receipts.get(h) or {}
            st = r.get("status")
            if st is None:
                continue
            # EVM convention: "0x0" fail, "0x1" success
            if isinstance(st, str) and st.lower() == "0x0":
                failures += 1
                if len(samples) < 10:
                    samples.append(h)

        if failures == 0:
            return []

        ratio = failures / max(1, len(ctx.tx_hashes))
        return [
            {
                "kind": "failure_burst",
                "failures": failures,
                "ratio": ratio,
                "sample_txs": samples,
                "reason": "Elevated revert/failure density may indicate contention or unstable contracts.",
                "strength": min(1.0, ratio * 2.0),
            }
        ]
