import logging
from pathlib import Path

import psycopg
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.config import settings
from app.db import SessionLocal, engine
from app.logging_config import setup_logging
from app.models import Department, HiredEmployee, Job
from app.services.rejection_log import log_rejected
from app.services.validation import validate_department, validate_hired_employee, validate_job

logger = logging.getLogger(__name__)

DATA_DIR = Path("data")

TABLES = [
    {
        "csv": DATA_DIR / "departments.csv",
        "staging": "staging.departments",
        "columns": ["id", "department"],
        "model": Department,
        "validate": validate_department,
    },
    {
        "csv": DATA_DIR / "jobs.csv",
        "staging": "staging.jobs",
        "columns": ["id", "job"],
        "model": Job,
        "validate": validate_job,
    },
    {
        "csv": DATA_DIR / "hired_employees.csv",
        "staging": "staging.hired_employees",
        "columns": ["id", "name", "datetime", "department_id", "job_id"],
        "model": HiredEmployee,
        "validate": validate_hired_employee,
    },
]


def create_staging_table(staging: str, columns: list[str]) -> None:
    logger.info("creando tabla de staging: %s", staging)
    cols_sql = ", ".join(f"{col} TEXT" for col in columns)
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))
        conn.execute(text(f"DROP TABLE IF EXISTS {staging}"))
        conn.execute(text(f"CREATE TABLE {staging} ({cols_sql})"))
        conn.commit()


def drop_staging_table(staging: str) -> None:
    with engine.connect() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {staging}"))
        conn.commit()


def copy_csv_to_staging(
    csv_path: Path, staging: str, columns: list[str], delimiter: str = settings.csv_delimiter
) -> None:
    if len(delimiter) != 1:
        raise ValueError(f"CSV delimiter must be a single character, got {delimiter!r}")

    dsn = settings.database_url.replace("postgresql+psycopg", "postgresql")
    cols_sql = ", ".join(columns)
    copy_sql = f"COPY {staging} ({cols_sql}) FROM STDIN WITH (FORMAT csv, DELIMITER '{delimiter}')"
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        with cur.copy(copy_sql) as copy:
            with csv_path.open("rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    copy.write(chunk)


def process_table(spec: dict) -> tuple[int, int, int]:
    staging = spec["staging"]
    columns = spec["columns"]
    model = spec["model"]
    table_name = model.__tablename__
    delimiter = spec.get("delimiter", settings.csv_delimiter)

    create_staging_table(staging, columns)
    copy_csv_to_staging(spec["csv"], staging, columns, delimiter)

    inserted_count = 0
    duplicate_count = 0
    rejected_count = 0
    db = SessionLocal()
    try:
        rows = db.execute(text(f"SELECT {', '.join(columns)} FROM {staging}")).mappings().all()

        for raw_row in rows:
            row = dict(raw_row)
            result = spec["validate"](row, db)

            if not result.valid:
                log_rejected(table_name, row, result.errors)
                rejected_count += 1
                continue

            stmt = (
                pg_insert(model)
                .values(**result.data)
                .on_conflict_do_nothing(index_elements=["id"])
                .returning(model.id)
            )
            row_landed = db.execute(stmt).first() is not None

            if row_landed:
                inserted_count += 1
            else:
                duplicate_count += 1

        db.commit()
    finally:
        db.close()

    # drop_staging_table(staging) # comment if you want to see the staging tables
    return inserted_count, duplicate_count, rejected_count


def main() -> None:
    setup_logging()
    for spec in TABLES:
        table_name = spec["model"].__tablename__
        inserted_count, duplicate_count, rejected_count = process_table(spec)
        logger.info(
            "%s: %d inserted, %d already existed, %d rejected",
            table_name,
            inserted_count,
            duplicate_count,
            rejected_count,
        )


if __name__ == "__main__":
    main()
