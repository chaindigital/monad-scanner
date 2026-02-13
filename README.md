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

## Configuration

The service uses a YAML config file (recommended):

- copy from `configs/config.example.yaml` → `configs/config.yaml`
- set your Monad **RPC URL** and **DB URL**
- toggle analyzers and the minimum stored severity threshold

Example:

```yaml
rpc:
  url: "https://rpc.monad.xyz"

db:
  url: "postgresql+psycopg://scanner:scanner@localhost:5432/monad_scanner"

analysis:
  ordering_sensitivity: true
  conflict_patterns: true
  hot_state: true
  hidden_dependencies: true

signals:
  min_severity_to_store: 20
```

---

## Quickstart (local)

### Requirements
- Python 3.11+
- Docker (optional, for Postgres)

### 1) Create config
```bash
cp configs/config.example.yaml configs/config.yaml
```

### 2) Start Postgres (optional)
```bash
docker-compose up -d db
```

### 3) Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

### 4) Run migrations
```bash
alembic upgrade head
```

### 5) Run the service (API + scanner)
```bash
python -m scanner.main
```

Default API address:
- `http://localhost:8080`

---

## Docker

Build and run:

```bash
docker-compose up --build
```

---

## API endpoints

Base path: `/v1`

### Health
`GET /v1/health`

Response:
```json
{"ok": true}
```

### Latest observed block
`GET /v1/blocks/latest`

### Scans
`GET /v1/scans?limit=50`

### Signals
`GET /v1/signals?severity_gte=60&category=ordering`

Signal fields:
- `signal_id`
- `block_number`
- `category`
- `severity`
- `confidence`
- `title`
- `explanation`
- `evidence`
- `recommended_actions`

---

## How signals map to real risk

### Ordering sensitivity
Ordering risk emerges when outcomes vary based on adjacency/ordering:
- shared-state patterns
- implicit sequencing assumptions
- contention and non-deterministic interference under load

### Conflict / failure bursts
A failure burst is often a symptom of:
- shared resources (nonces, allowances, shared state locks)
- unstable execution paths (edge cases under load)
- hot contracts with high write pressure

### Hot state
Hot state zones can degrade throughput and amplify interference:
- a small number of keys/contracts dominate writes
- event-topic repetition indicates concentrated flows
- hotspots correlate with transient performance cliffs

### Hidden dependencies
Hidden coupling creates “surprise” cascades:
- transaction flows become implicitly linked
- one path’s failure increases probability of another’s failure
- under load, coupling amplifies instability

---

## Data availability notes (Monad)

The scanner is designed for **progressive enrichment**:

- **Minimal mode:** blocks + tx hashes
- **Enhanced mode:** receipts + logs (if RPC supports it)
- **Full mode:** execution traces (addable via provider interface)

RPC adapters live in:
- `src/scanner/rpc/monad_client.py`

---

## Extending the scanner

### Add a new analyzer
1. Create a module in `src/scanner/analyzers/`
2. Implement `analyze(ctx)` to return findings
3. Wire it in `PipelineRunner` and add config toggle

### Improve scoring/explanations
- scoring: `src/scanner/signals/scorer.py`
- explanations: `src/scanner/signals/explain.py`

---

## Security considerations
- Use a trusted RPC endpoint with rate limits and authentication (if possible)
- Configure strict timeouts and retries
- Consider splitting into two services for production:
  - API service (read-only)
  - worker service (scanner loop)
