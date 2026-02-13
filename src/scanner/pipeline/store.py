from __future__ import annotations

import logging
from typing import Iterable

from sqlalchemy import select

from scanner.db.models import Block, Scan, Signal
from scanner.db.session import SessionLocal
from scanner.utils.time import utcnow

log = logging.getLogger("scanner.pipeline.store")


class Store:
    def __init__(self, chain_id: str) -> None:
        self.chain_id = chain_id

    def upsert_block(self, number: int, block_hash: str, parent_hash: str | None, timestamp, raw, tx_count: int) -> None:
        db = SessionLocal()
        try:
            existing = db.execute(select(Block).where(Block.hash == block_hash)).scalar_one_or_none()
            if existing:
                return
            b = Block(
                chain_id=self.chain_id,
                number=number,
                hash=block_hash,
                parent_hash=parent_hash,
                timestamp=timestamp,
                tx_count=tx_count,
                raw=raw,
                created_at=utcnow(),
            )
            db.add(b)
            db.commit()
        finally:
            db.close()

    def start_scan(self, block_number: int, block_hash: str) -> int:
        db = SessionLocal()
        try:
            s = Scan(
                chain_id=self.chain_id,
                block_number=block_number,
                block_hash=block_hash,
                status="running",
                started_at=utcnow(),
                finished_at=None,
                meta=None,
            )
            db.add(s)
            db.commit()
            db.refresh(s)
            return int(s.id)
        finally:
            db.close()

    def finish_scan(self, scan_id: int, status: str, meta: dict | None = None) -> None:
        db = SessionLocal()
        try:
            s = db.get(Scan, scan_id)
            if not s:
                return
            s.status = status
            s.finished_at = utcnow()
            s.meta = meta
            db.commit()
        finally:
            db.close()

    def insert_signals(self, signals: Iterable[Signal]) -> int:
        db = SessionLocal()
        inserted = 0
        try:
            for sig in signals:
                exists = db.execute(select(Signal).where(Signal.signal_id == sig.signal_id)).scalar_one_or_none()
                if exists:
                    continue
                db.add(sig)
                inserted += 1
            db.commit()
            return inserted
        finally:
            db.close()
