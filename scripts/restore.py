"""Restore one table, or all of them in dependency order, from their AVRO backups.

Usage:
    uv run python -m scripts.restore departments
    uv run python -m scripts.restore --all
"""

import argparse
import logging

from app.db import SessionLocal
from app.logging_config import setup_logging
from app.services.avro_backup import MODELS
from app.services.avro_restore import restore_all_from_avro, restore_table_from_avro

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("table", nargs="?", choices=list(MODELS), help="table to restore (omit when using --all)")
    parser.add_argument("--all", action="store_true", help="restore all tables in dependency order")
    args = parser.parse_args()

    if not args.all and not args.table:
        parser.error("either specify a table or use --all")

    db = SessionLocal()
    try:
        if args.all:
            counts = restore_all_from_avro(db)
            for table_name, count in counts.items():
                logger.info("%s: %d records restored", table_name, count)
        else:
            count = restore_table_from_avro(db, args.table)
            logger.info("%s: %d records restored", args.table, count)
    finally:
        db.close()


if __name__ == "__main__":
    main()
