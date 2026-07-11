from pydantic import BaseModel


class RejectedRecord(BaseModel):
    row: dict
    errors: list[str]


class IngestResponse(BaseModel):
    inserted: int
    rejected: int
    rejected_records: list[RejectedRecord] = []
