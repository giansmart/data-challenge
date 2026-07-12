from pydantic import BaseModel


class RejectedRecord(BaseModel):
    row: dict
    errors: list[str]


class IngestResponse(BaseModel):
    inserted: int
    rejected: int
    rejected_records: list[RejectedRecord] = []


class HiresByQuarterRow(BaseModel):
    department: str
    job: str
    Q1: int
    Q2: int
    Q3: int
    Q4: int


class DepartmentAboveAverageRow(BaseModel):
    id: int
    department: str
    hired: int
