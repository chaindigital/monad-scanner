from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Engine is created from env override if present; otherwise from YAML config in runtime.
DEFAULT_DB_URL = os.environ.get(
    "SCANNER_DB_URL",
    "postgresql+psycopg://scanner:scanner@localhost:5432/monad_scanner",
)

_engine = create_engine(DEFAULT_DB_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def set_db_url(db_url: str) -> None:
    global _engine, SessionLocal
    _engine = create_engine(db_url, future=True, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def get_engine():
    return _engine
