from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.dto import DepartmentAboveAverageRow, HiresByQuarterRow
from app.services.analytics import get_departments_above_average, get_hires_by_quarter

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/hires-by-quarter", response_model=list[HiresByQuarterRow])
def hires_by_quarter(db: Session = Depends(get_db)) -> list[HiresByQuarterRow]:
    return get_hires_by_quarter(db)


@router.get("/departments-above-average", response_model=list[DepartmentAboveAverageRow])
def departments_above_average(db: Session = Depends(get_db)) -> list[DepartmentAboveAverageRow]:
    return get_departments_above_average(db)
