from typing import Callable

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.dto import IngestResponse, RejectedRecord
from app.services.rejection_log import log_rejected
from app.services.validation import ValidationResult


def ingest_batch(
    db: Session,
    table_name: str,
    model: type,
    validate_fn: Callable[[dict, Session], ValidationResult],
    records: list[dict],
) -> IngestResponse:
    inserted = 0
    rejected_records: list[RejectedRecord] = []

    for row in records:
        result = validate_fn(row, db)

        if not result.valid:
            log_rejected(table_name, row, result.errors)
            rejected_records.append(RejectedRecord(row=row, errors=result.errors))
            continue

        stmt = (
            pg_insert(model)
            .values(**result.data)
            .on_conflict_do_nothing(index_elements=["id"])
            .returning(model.id)
        )
        row_landed = db.execute(stmt).first() is not None

        if not row_landed:
            errors = [f"id {result.data['id']} already exists (duplicate in table or within this batch)"]
            log_rejected(table_name, row, errors)
            rejected_records.append(RejectedRecord(row=row, errors=errors))
            continue

        inserted += 1

    db.commit()
    return IngestResponse(inserted=inserted, rejected=len(rejected_records), rejected_records=rejected_records)
