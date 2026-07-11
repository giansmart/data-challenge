from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.dto import IngestResponse
from app.models import Department, HiredEmployee, Job
from app.services.ingestion import ingest_batch
from app.services.validation import validate_department, validate_hired_employee, validate_job

router = APIRouter(tags=["ingestion"])

BatchBody = Annotated[list[dict], Body(min_length=1, max_length=settings.max_batch_size)]


@router.post("/departments", response_model=IngestResponse)
def ingest_departments(records: BatchBody, db: Session = Depends(get_db)) -> IngestResponse:
    return ingest_batch(db, "departments", Department, validate_department, records)


@router.post("/jobs", response_model=IngestResponse)
def ingest_jobs(records: BatchBody, db: Session = Depends(get_db)) -> IngestResponse:
    return ingest_batch(db, "jobs", Job, validate_job, records)


@router.post("/hired-employees", response_model=IngestResponse)
def ingest_hired_employees(records: BatchBody, db: Session = Depends(get_db)) -> IngestResponse:
    return ingest_batch(db, "hired_employees", HiredEmployee, validate_hired_employee, records)
