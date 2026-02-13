from __future__ import annotations

import logging
from logging.config import dictConfig
from pathlib import Path

import yaml


def setup_logging(logging_yaml_path: str | None = None, default_level: str = "INFO") -> None:
    if logging_yaml_path:
        p = Path(logging_yaml_path)
        if p.exists():
            cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
            dictConfig(cfg)
            return

    # Fallback: simple config (useful for minimal deploys)
    logging.basicConfig(
        level=getattr(logging, default_level.upper(), logging.INFO),
        format="%(levelname)s %(asctime)s %(name)s :: %(message)s",
    )
