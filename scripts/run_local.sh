#!/usr/bin/env bash
set -euo pipefail

export SCANNER_CONFIG="${SCANNER_CONFIG:-configs/config.yaml}"
export SCANNER_DB_URL="${SCANNER_DB_URL:-postgresql+psycopg://scanner:scanner@localhost:5432/monad_scanner}"

alembic upgrade head
python -m scanner.main
