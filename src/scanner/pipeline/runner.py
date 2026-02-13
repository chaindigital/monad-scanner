from __future__ import annotations

import logging
from typing import Any

from scanner.analyzers import (
    ConflictPatternsAnalyzer,
    HiddenDependenciesAnalyzer,
    HotStateAnalyzer,
    OrderingSensitivityAnalyzer,
)
from scanner.analyzers.base import AnalyzerContext
from scanner.db.models import Signal
from scanner.pipeline.store import Store
from scanner.rpc.monad_client import MonadClient
from scanner.signals.scorer import to_draft
from scanner.signals import explain
from scanner.utils.hashing import stable_hash
from scanner.utils.time import utcnow

log = logging.getLogger("scanner.pipeline.runner")


class PipelineRunner:
    def __init__(self, chain_id: str, client: MonadClient, store: Store, cfg: dict[str, Any]) -> None:
        self.chain_id = chain_id
        self.client = client
        self.store = store
        self.cfg = cfg

        self.ordering = OrderingSensitivityAnalyzer()
        self.conflict = ConflictPatternsAnalyzer()
        self.hot = HotStateAnalyzer()
        self.dep = HiddenDependenciesAnalyzer()

    async def process_block(self, block_number: int) -> None:
        b = await self.client.get_block_by_number(block_number)
        self.store.upsert_block(
            number=b.number,
            block_hash=b.hash,
            parent_hash=b.parent_hash,
            timestamp=b.timestamp,
            raw=b.raw,
            tx_count=len(b.tx_hashes),
        )

        scan_id = self.store.start_scan(block_number=b.number, block_hash=b.hash)
        try:
            receipts = await self._fetch_receipts(b.tx_hashes)
            ctx = AnalyzerContext(
                chain_id=self.chain_id,
                block_number=b.number,
                block_hash=b.hash,
                tx_hashes=b.tx_hashes,
                receipts=receipts,
                raw_block=b.raw,
            )

            findings = []
            if self.cfg.get("ordering_sensitivity", True):
                findings += [("ordering", x) for x in await self.ordering.analyze(ctx)]
            if self.cfg.get("conflict_patterns", True):
                findings += [("conflict", x) for x in await self.conflict.analyze(ctx)]
            if self.cfg.get("hot_state", True):
                findings += [("hot_state", x) for x in await self.hot.analyze(ctx)]
            if self.cfg.get("hidden_dependencies", True):
                findings += [("dependency", x) for x in await self.dep.analyze(ctx)]

            signals = self._to_signals(ctx, findings)
            inserted = self.store.insert_signals(signals)
            self.store.finish_scan(scan_id, "success", meta={"signals_inserted": inserted})
        except Exception as e:
            log.exception("Scan failed block=%s err=%s", block_number, e)
            self.store.finish_scan(scan_id, "fail", meta={"error": str(e)})

    async def _fetch_receipts(self, tx_hashes: list[str]) -> dict[str, dict | None]:
        receipts: dict[str, dict | None] = {}
        # Keep it safe: don't explode RPC if blocks are heavy.
        for h in tx_hashes[:5000]:
            receipts[h] = await self.client.get_receipt(h)
        return receipts

    def _to_signals(self, ctx: AnalyzerContext, findings: list[tuple[str, dict]]) -> list[Signal]:
        out: list[Signal] = []
        min_sev = int(self.cfg.get("min_severity_to_store", 20))

        for category, f in findings:
            kind = f.get("kind", "unknown")
            strength = float(f.get("strength", 0.2))

            if category == "ordering":
                msg, actions, evidence = explain.explain_ordering(f)
            elif category == "conflict":
                msg, actions, evidence = explain.explain_conflict(f)
            elif category == "hot_state":
                msg, actions, evidence = explain.explain_hot_state(f)
            elif category == "dependency":
                msg, actions, evidence = explain.explain_dependency(f)
            else:
                msg, actions, evidence = "Risk pattern detected.", ["Investigate relevant tx cluster."], f

            draft = to_draft(
                category=category,
                kind=kind,
                strength=strength,
                explanation=msg,
                evidence=evidence,
                actions=actions,
            )

            if draft.severity < min_sev:
                continue

            sid = stable_hash(ctx.chain_id, str(ctx.block_number), category, kind, str(draft.severity))
            out.append(
                Signal(
                    signal_id=sid,
                    chain_id=ctx.chain_id,
                    block_number=ctx.block_number,
                    category=draft.category,
                    severity=draft.severity,
                    confidence=draft.confidence,
                    title=draft.title,
                    explanation=draft.explanation,
                    evidence=draft.evidence,
                    recommended_actions=draft.recommended_actions,
                    created_at=utcnow(),
                )
            )

        return out
