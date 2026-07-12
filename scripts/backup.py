"""Export the full content of every table to an AVRO file on the filesystem.

Usage: uv run python -m scripts.backup
"""

import logging

from app.db import SessionLocal
from app.logging_config import setup_logging
from app.services.avro_backup import MODELS, export_table_to_avro

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    db = SessionLocal()
    try:
        for table_name in MODELS:
            file_path = export_table_to_avro(db, table_name)
            logger.info("backup de %s guardado en %s", table_name, file_path)
    finally:
        db.close()


if __name__ == "__main__":
    main()
