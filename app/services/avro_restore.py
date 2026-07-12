import logging
from pathlib import Path

import fastavro
from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import engine
from app.services.avro_backup import MODELS

logger = logging.getLogger(__name__)

TABLE_ORDER = {
    "departments": 0,
    "jobs": 0,
    "hired_employees": 1,
}


def _load_avro_records(table_name: str) -> list[dict]:
    file_path = Path(settings.backup_dir) / f"{table_name}.avro"
    if not file_path.exists():
        raise FileNotFoundError(f"no backup found at {file_path}")

    with file_path.open("rb") as f:
        return list(fastavro.reader(f))


def restore_table_from_avro(db: Session, table_name: str) -> int:
    if table_name not in MODELS:
        raise ValueError(f"unknown table {table_name!r}")

    model = MODELS[table_name]
    model.__table__.create(bind=engine, checkfirst=True)

    records = _load_avro_records(table_name)

    db.execute(text(f"DELETE FROM {model.__tablename__}"))
    if records:
        db.execute(insert(model), records)
    db.commit()

    return len(records)


def restore_all_from_avro(db: Session) -> dict[str, int]:
    insert_order = sorted(TABLE_ORDER, key=lambda t: TABLE_ORDER[t])
    clear_order = sorted(TABLE_ORDER, key=lambda t: TABLE_ORDER[t], reverse=True)

    for table_name in insert_order:
        MODELS[table_name].__table__.create(bind=engine, checkfirst=True)

    for table_name in clear_order:
        db.execute(text(f"DELETE FROM {MODELS[table_name].__tablename__}"))

    counts: dict[str, int] = {}
    for table_name in insert_order:
        records = _load_avro_records(table_name)
        if records:
            db.execute(insert(MODELS[table_name]), records)
        counts[table_name] = len(records)

    db.commit()
    return counts
