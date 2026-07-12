"""Export full table contents to AVRO files on the filesystem."""

from pathlib import Path

import fastavro
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Department, HiredEmployee, Job

MODELS = {
    "departments": Department,
    "jobs": Job,
    "hired_employees": HiredEmployee,
}

SCHEMAS = {
    "departments": {
        "type": "record",
        "name": "Department",
        "fields": [
            {"name": "id", "type": "int"},
            {"name": "department", "type": "string"},
        ],
    },
    "jobs": {
        "type": "record",
        "name": "Job",
        "fields": [
            {"name": "id", "type": "int"},
            {"name": "job", "type": "string"},
        ],
    },
    "hired_employees": {
        "type": "record",
        "name": "HiredEmployee",
        "fields": [
            {"name": "id", "type": "int"},
            {"name": "name", "type": "string"},
            {"name": "datetime", "type": {"type": "long", "logicalType": "timestamp-millis"}},
            {"name": "department_id", "type": "int"},
            {"name": "job_id", "type": "int"},
        ],
    },
}


def export_table_to_avro(db: Session, table_name: str) -> Path:
    if table_name not in MODELS:
        raise ValueError(f"unknown table {table_name!r}")

    model = MODELS[table_name]
    schema = SCHEMAS[table_name]
    columns = [c.name for c in model.__table__.columns]

    rows = db.execute(select(model)).scalars().all()
    records = [{col: getattr(row, col) for col in columns} for row in rows]

    backup_dir = Path(settings.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    file_path = backup_dir / f"{table_name}.avro"

    with file_path.open("wb") as f:
        fastavro.writer(f, schema, records)

    return file_path
