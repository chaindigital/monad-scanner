from __future__ import annotations

import argparse
import os
import sys

from scanner.settings import Settings


def main() -> None:
    p = argparse.ArgumentParser(prog="monad-scanner", description="Chain Digital — Monad risk scanner")
    p.add_argument("--print-config", action="store_true", help="Print parsed YAML config and exit")
    args = p.parse_args()

    s = Settings()
    cfg = s.load()

    if args.print_config:
        print(cfg.model_dump())
        sys.exit(0)

    # Lightweight CLI entry point; main runtime starts in scanner.main.
    os.execvp("python", ["python", "-m", "scanner.main"])


if __name__ == "__main__":
    main()
