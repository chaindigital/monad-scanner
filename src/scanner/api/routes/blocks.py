from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from scanner.api.deps import get_db
from scanner.db.models import Block

router = APIRouter(tags=["blocks"])


@router.get("/blocks/latest")
def latest_block(db: Session = Depends(get_db)):
    b = db.execute(select(Block).order_by(desc(Block.number)).limit(1)).scalar_one_or_none()
    if not b:
        return {"latest": None}
    return {
        "latest": {
            "chain_id": b.chain_id,
            "number": b.number,
            "hash": b.hash,
            "timestamp": b.timestamp,
            "tx_count": b.tx_count,
        }
    }
