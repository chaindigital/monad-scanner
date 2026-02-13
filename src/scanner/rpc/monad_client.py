from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from scanner.rpc.jsonrpc import JsonRpcClient
from scanner.rpc.types import BlockRef

log = logging.getLogger("scanner.rpc.monad")


class MonadClient:
    """
    Thin wrapper around JSON-RPC. Method names are intentionally abstracted:
    you can adapt them to a Monad-compatible RPC surface without touching analyzers.
    """

    def __init__(self, rpc: JsonRpcClient) -> None:
        self.rpc = rpc

    async def get_latest_block_number(self) -> int:
        # Common EVM-style: eth_blockNumber
        n_hex = await self.rpc.call("eth_blockNumber")
        return int(n_hex, 16)

    async def get_block_by_number(self, number: int) -> BlockRef:
        # Common EVM-style: eth_getBlockByNumber
        block: dict[str, Any] = await self.rpc.call("eth_getBlockByNumber", [hex(number), False])
        if not block:
            raise RuntimeError(f"Block not found: {number}")

        ts = None
        if "timestamp" in block and block["timestamp"] is not None:
            try:
                ts = datetime.fromtimestamp(int(block["timestamp"], 16), tz=timezone.utc)
            except Exception:
                ts = None

        txs = block.get("transactions") or []
        tx_hashes = [t if isinstance(t, str) else t.get("hash") for t in txs]
        tx_hashes = [h for h in tx_hashes if h]

        return BlockRef(
            number=int(block["number"], 16),
            hash=block.get("hash", ""),
            parent_hash=block.get("parentHash"),
            timestamp=ts,
            tx_hashes=tx_hashes,
            raw=block,
        )

    async def get_receipt(self, tx_hash: str) -> dict[str, Any] | None:
        # Common EVM-style: eth_getTransactionReceipt
        try:
            r = await self.rpc.call("eth_getTransactionReceipt", [tx_hash])
            return r
        except Exception as e:
            # Receipts may be temporarily unavailable depending on node configuration.
            log.debug("Receipt unavailable tx=%s err=%s", tx_hash, e)
            return None
