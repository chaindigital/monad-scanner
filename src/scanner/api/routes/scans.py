from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from scanner.api.deps import get_db
from scanner.db.models import Scan

router = APIRouter(tags=["scans"])


@router.get("/scans")
def list_scans(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = db.execute(select(Scan).order_by(desc(Scan.block_number)).limit(limit)).scalars().all()
    return {
        "items": [
            {
                "id": r.id,
                "chain_id": r.chain_id,
                "block_number": r.block_number,
                "block_hash": r.block_hash,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "meta": r.meta,
            }
            for r in rows
        ]
    }
