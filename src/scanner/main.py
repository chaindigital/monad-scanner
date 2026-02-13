from __future__ import annotations

import asyncio
import logging
import os

import uvicorn
from fastapi import FastAPI

from scanner.api import router as api_router
from scanner.db.session import set_db_url
from scanner.logging import setup_logging
from scanner.pipeline import PipelineRunner, Scheduler, Store
from scanner.rpc import JsonRpcClient, MonadClient
from scanner.settings import Settings

log = logging.getLogger("scanner.main")


def build_app() -> FastAPI:
    app = FastAPI(title="Chain Digital — Monad Risk Scanner", version="0.1.0")
    app.include_router(api_router)
    return app


async def run_scanner(cfg) -> None:
    chain_id = cfg.chain.id
    rpc = JsonRpcClient(cfg.rpc.url, timeout=cfg.rpc.timeout_seconds, max_retries=cfg.rpc.max_retries)
    client = MonadClient(rpc)
    store = Store(chain_id=chain_id)

    runner = PipelineRunner(
        chain_id=chain_id,
        client=client,
        store=store,
        cfg={
            "ordering_sensitivity": cfg.analysis.ordering_sensitivity,
            "conflict_patterns": cfg.analysis.conflict_patterns,
            "hot_state": cfg.analysis.hot_state,
            "hidden_dependencies": cfg.analysis.hidden_dependencies,
            "min_severity_to_store": cfg.signals.min_severity_to_store,
        },
    )

    confirmations = int(cfg.chain.confirmations or 0)
    max_blocks = int(cfg.scanner.max_blocks_per_tick)
    start_override = cfg.scanner.backfill_start_block

    state = {"next": None}

    async def tick(n: int) -> None:
        head = await client.get_latest_block_number()
        safe_head = max(0, head - confirmations)

        if state["next"] is None:
            state["next"] = int(start_override) if start_override is not None else safe_head
        # Catch up forward if we started behind
        if state["next"] < 0:
            state["next"] = 0

        processed = 0
        while processed < min(n, max_blocks) and state["next"] <= safe_head:
            bn = state["next"]
            await runner.process_block(bn)
            state["next"] = bn + 1
            processed += 1

    sched = Scheduler(
        poll_interval_seconds=cfg.scanner.poll_interval_seconds,
        max_blocks_per_tick=cfg.scanner.max_blocks_per_tick,
    )
    await sched.loop(tick)


async def main_async() -> None:
    s = Settings()
    cfg = s.load()

    setup_logging(logging_yaml_path="configs/logging.yaml", default_level=cfg.app.log_level)

    set_db_url(cfg.db.url)
    app = build_app()

    # Run both: API server + scanner loop in the same process (simple deploy).
    # For scale: split into separate services (api + worker) using the same codebase.
    config = uvicorn.Config(app, host=cfg.app.host, port=cfg.app.port, log_level=cfg.app.log_level.lower())
    server = uvicorn.Server(config)

    async def api_task():
        await server.serve()

    async def scanner_task():
        await run_scanner(cfg)

    await asyncio.gather(api_task(), scanner_task())


def main() -> None:
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        log.info("Shutdown requested.")


if __name__ == "__main__":
    # Support `python -m scanner.main`
    os.environ.setdefault("PYTHONASYNCIODEBUG", "0")
    main()
