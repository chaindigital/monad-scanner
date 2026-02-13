from __future__ import annotations

import hashlib


def stable_hash(*parts: str) -> str:
    # Deterministic IDs help de-duplication across restarts.
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"|")
    return h.hexdigest()
