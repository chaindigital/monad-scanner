from __future__ import annotations

from fastapi import APIRouter

from scanner.api.routes import blocks, health, scans, signals

router = APIRouter(prefix="/v1")
router.include_router(health.router)
router.include_router(blocks.router)
router.include_router(scans.router)
router.include_router(signals.router)
