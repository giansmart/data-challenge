from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.services.validation import validate_department, validate_hired_employee, validate_job


def _mock_db(department_exists: bool = True, job_exists: bool = True) -> MagicMock:
    db = MagicMock(spec=Session)
    db.scalar.side_effect = [
        1 if department_exists else None,
        1 if job_exists else None,
    ]
    return db


def test_validate_department_valid():
    result = validate_department({"id": "1", "department": "Engineering"})
    assert result.valid
    assert result.data == {"id": 1, "department": "Engineering"}


def test_validate_department_missing_name():
    result = validate_department({"id": "1", "department": ""})
    assert not result.valid
    assert "missing required field 'department'" in result.errors


def test_validate_job_missing_id():
    result = validate_job({"id": "", "job": "Recruiter"})
    assert not result.valid
    assert "missing required field 'id'" in result.errors


def test_validate_hired_employee_missing_name():
    result = validate_hired_employee(
        {"id": "1", "name": "", "datetime": "2021-07-27T16:02:08Z", "department_id": "1", "job_id": "1"},
        db=MagicMock(spec=Session),
    )
    assert not result.valid
    assert "missing required field 'name'" in result.errors


def test_validate_hired_employee_bad_iso_datetime():
    result = validate_hired_employee(
        {"id": "1", "name": "John", "datetime": "27/07/2021", "department_id": "1", "job_id": "1"},
        db=MagicMock(spec=Session),
    )
    assert not result.valid
    assert any("must be ISO 8601" in error for error in result.errors)


def test_validate_hired_employee_nonexistent_department():
    result = validate_hired_employee(
        {"id": "1", "name": "John", "datetime": "2021-07-27T16:02:08Z", "department_id": "9999", "job_id": "1"},
        db=_mock_db(department_exists=False, job_exists=True),
    )
    assert not result.valid
    assert "department_id 9999 does not exist" in result.errors


def test_validate_hired_employee_nonexistent_job():
    result = validate_hired_employee(
        {"id": "1", "name": "John", "datetime": "2021-07-27T16:02:08Z", "department_id": "1", "job_id": "9999"},
        db=_mock_db(department_exists=True, job_exists=False),
    )
    assert not result.valid
    assert "job_id 9999 does not exist" in result.errors


def test_validate_hired_employee_valid():
    result = validate_hired_employee(
        {"id": "1", "name": "John", "datetime": "2021-07-27T16:02:08Z", "department_id": "1", "job_id": "1"},
        db=_mock_db(department_exists=True, job_exists=True),
    )
    assert result.valid
    assert result.errors == []
