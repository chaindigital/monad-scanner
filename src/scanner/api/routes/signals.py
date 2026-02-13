from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from scanner.api.deps import get_db
from scanner.db.models import Signal

router = APIRouter(tags=["signals"])


@router.get("/signals")
def list_signals(
    limit: int = Query(default=50, ge=1, le=500),
    severity_gte: int = Query(default=0, ge=0, le=100),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    conds = [Signal.severity >= severity_gte]
    if category:
        conds.append(Signal.category == category)

    rows = (
        db.execute(select(Signal).where(and_(*conds)).order_by(desc(Signal.block_number)).limit(limit))
        .scalars()
        .all()
    )

    return {
        "items": [
            {
                "signal_id": r.signal_id,
                "chain_id": r.chain_id,
                "block_number": r.block_number,
                "category": r.category,
                "severity": r.severity,
                "confidence": r.confidence,
                "title": r.title,
                "explanation": r.explanation,
                "evidence": r.evidence,
                "recommended_actions": r.recommended_actions,
                "created_at": r.created_at,
            }
            for r in rows
        ]
    }
