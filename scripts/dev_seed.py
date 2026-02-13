#!/usr/bin/env python3
from __future__ import annotations

import os
from datetime import datetime, timezone

from scanner.db.session import SessionLocal
from scanner.db.models import Signal

# Tiny dev helper to validate API rendering quickly.

def main() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        s = Signal(
            signal_id="dev:signal:ordering:1",
            chain_id=os.environ.get("CHAIN_ID", "monad-mainnet"),
            block_number=123,
            category="ordering",
            severity=72,
            confidence=0.77,
            title="High ordering sensitivity cluster detected",
            explanation="A set of transactions exhibits outcome variance correlated with adjacency and ordering.",
            evidence={"txs": ["0xaaa", "0xbbb"], "heuristic": "adjacency-correlation"},
            recommended_actions=[
                "For dApps: reduce shared-state contention; isolate hot writes; avoid order-dependent reads.",
                "For ops: monitor failure bursts and reorg-like symptoms; consider mempool policies if applicable.",
            ],
            created_at=now,
        )
        db.add(s)
        db.commit()
        print("Seeded 1 dev signal.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
