from __future__ import annotations

from collections import defaultdict

from scanner.analyzers.base import AnalyzerContext


class HiddenDependenciesAnalyzer:
    name = "hidden_dependencies"

    async def analyze(self, ctx: AnalyzerContext) -> list[dict]:
        # Build a weak dependency graph based on shared "to" and shared first-topic.
        groups = defaultdict(list)

        for h in ctx.tx_hashes:
            r = ctx.receipts.get(h) or {}
            to = (r.get("to") or "").lower()
            logs = r.get("logs") or []
            t0 = None
            if logs and isinstance(logs, list):
                topics = (logs[0].get("topics") or []) if isinstance(logs[0], dict) else []
                if topics:
                    t0 = topics[0].lower()

            if to:
                groups[f"to:{to}"].append(h)
            if t0:
                groups[f"topic:{t0}"].append(h)

        # Find non-trivial groups
        findings = []
        for k, txs in groups.items():
            if len(txs) >= 8:
                findings.append({"key": k, "txs": txs[:50]})

        if not findings:
            return []

        return [
            {
                "kind": "coupling_groups",
                "groups": findings[:10],
                "reason": "Multiple txs share implicit resources; hidden coupling risk increases under load.",
                "strength": min(1.0, 0.25 + 0.02 * len(findings)),
            }
        ]
