# Chain Digital — Monad Execution & State Risk Scanner 🧠⛓️

**Chain Digital** is a validator operator and infrastructure team focused on reliability, performance, and risk visibility across modern high-throughput networks.

This repository contains a production-style backend service that continuously scans Monad to surface **execution-layer** and **state-layer** risk zones. The scanner automatically analyzes **blocks**, **transactions within blocks**, **transaction receipts/log hints**, and derived execution features to detect:

- **Unstable behavioral shifts** (sudden changes in execution characteristics)
- **Conflict patterns** (contention-like behavior, repeated failures, collisions)
- **Ordering sensitivity** (high sensitivity to transaction order within blocks)
- **Hot state zones** (overloaded state segments / concentrated write pressure)
- **Hidden dependencies** (non-obvious coupling between transactions)

The service generates **actionable signals**: *where risk emerges, why it appears, and what mitigations reduce the likelihood of latent conflicts under load*.

---

## Why this exists

High-throughput execution environments often exhibit failure modes that are invisible at low traffic:
- race-like ordering effects,
- state hotspots (a small subset of storage dominating write volume),
- dependency cascades between unrelated transaction flows,
- revert bursts caused by shared resources or tight coupling.

This scanner is designed to reveal those zones early and provide a structured view of technical risk in the Monad ecosystem.

---

## Core capabilities

### Continuous chain ingestion
- Pulls latest blocks via JSON-RPC
- Extracts transaction hashes and (optionally) receipts/log hints
- Persists block observations + analysis metadata

### Modular analysis pipeline
Analyzer modules run per-block and produce normalized findings:
- `ordering_sensitivity`: order-dependent variance hints inside the same block
- `conflict_patterns`: failure/revert bursts and contention-like signatures
- `hot_state`: approximates hot zones via repeated targets/topics and write-intensity heuristics
- `hidden_dependencies`: identifies coupling clusters using weak dependency graphs

### Risk signals (operator-grade output)
Signals are standardized across categories:
- `severity` (0–100)
- `confidence` (0–1)
- `category` (`ordering`, `conflict`, `hot_state`, `dependency`, `shift`)
- `explanation` (human-readable, technical)
- `evidence` (compact JSON payload for dashboards)
- `recommended_actions` (practical mitigation steps)

---

## Architecture

**Tech stack**
- **FastAPI** — HTTP API layer
- **SQLAlchemy + Alembic** — persistence and schema migrations
- **Uvicorn** — ASGI runtime
- **httpx** — RPC networking with timeouts/retries

**Separation of concerns**
- `src/scanner/rpc` — JSON-RPC client + Monad adapter
- `src/scanner/pipeline` — scheduler + runner + storage orchestration
- `src/scanner/analyzers` — pluggable analysis modules
- `src/scanner/signals` — scoring + explanation + normalization
- `src/scanner/api` — REST routes for scans/signals/health

**Operational posture**
- deterministic signal IDs to avoid duplicates after restarts
- RPC backoff + jitter to survive noisy endpoints
- idempotent ingestion keyed by block hash/number
- structured JSON-friendly logging

---

## Repository layout

```text
src/scanner/
  api/                 # FastAPI routes and wiring
  analyzers/           # analysis modules (pluggable)
  db/                  # SQLAlchemy models + session
  pipeline/            # scanner loop + runner
  rpc/                 # JSON-RPC + Monad adapter
  signals/             # scoring + explanations + schema
  utils/               # time/hashing/backoff helpers
  main.py              # single-process runtime (api + scanner)
```

