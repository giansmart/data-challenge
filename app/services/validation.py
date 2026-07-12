from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Department, Job


@dataclass
class ValidationResult:
    valid: bool
    data: dict | None = None
    errors: list[str] = field(default_factory=list)


def _require_fields(row: dict, fields: list[str]) -> list[str]:
    errors = []
    for f in fields:
        value = row.get(f)
        if value is None or str(value).strip() == "":
            errors.append(f"missing required field '{f}'")
    return errors


def _parse_int(row: dict, field_name: str, errors: list[str]) -> int | None:
    raw = row.get(field_name)
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        errors.append(f"'{field_name}' must be an integer, got {raw!r}")
        return None


def _parse_iso_datetime(raw: str, errors: list[str]) -> datetime | None:
    try:
        return datetime.fromisoformat(str(raw).strip())
    except ValueError:
        errors.append(f"'datetime' must be ISO 8601, got {raw!r}")  # what is it?
        return None


def validate_department(row: dict, db: Session | None = None) -> ValidationResult:
    errors = _require_fields(row, ["id", "department"])
    if errors:
        return ValidationResult(valid=False, errors=errors)

    dept_id = _parse_int(row, "id", errors)
    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(
        valid=True,
        data={"id": dept_id, "department": str(row["department"]).strip()},
    )


def validate_job(row: dict, db: Session | None = None) -> ValidationResult:
    errors = _require_fields(row, ["id", "job"])
    if errors:
        return ValidationResult(valid=False, errors=errors)

    job_id = _parse_int(row, "id", errors)
    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(
        valid=True,
        data={"id": job_id, "job": str(row["job"]).strip()},
    )


def validate_hired_employee(row: dict, db: Session) -> ValidationResult:
    errors = _require_fields(row, ["id", "name", "datetime", "department_id", "job_id"])
    if errors:
        return ValidationResult(valid=False, errors=errors)

    emp_id = _parse_int(row, "id", errors)
    department_id = _parse_int(row, "department_id", errors)
    job_id = _parse_int(row, "job_id", errors)
    hired_at = _parse_iso_datetime(row["datetime"], errors)
    if errors:
        return ValidationResult(valid=False, errors=errors)

    if db.scalar(select(Department.id).where(Department.id == department_id)) is None:
        errors.append(f"department_id {department_id} does not exist")

    if db.scalar(select(Job.id).where(Job.id == job_id)) is None:
        errors.append(f"job_id {job_id} does not exist")

    if errors:
        return ValidationResult(valid=False, errors=errors)

    return ValidationResult(
        valid=True,
        data={
            "id": emp_id,
            "name": str(row["name"]).strip(),
            "datetime": hired_at,
            "department_id": department_id,
            "job_id": job_id,
        },
    )
