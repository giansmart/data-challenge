"""Analytics queries for Challenge #2, computed via raw parametrized SQL."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dto import DepartmentAboveAverageRow, HiresByQuarterRow

_HIRES_BY_QUARTER_SQL = text("""
    SELECT
        d.department,
        j.job,
        COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM he.datetime) = 1) AS q1,
        COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM he.datetime) = 2) AS q2,
        COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM he.datetime) = 3) AS q3,
        COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM he.datetime) = 4) AS q4
    FROM hired_employees he
    JOIN departments d ON d.id = he.department_id
    JOIN jobs j ON j.id = he.job_id
    WHERE EXTRACT(YEAR FROM he.datetime) = :year
    GROUP BY d.department, j.job
    ORDER BY d.department, j.job
""")

_DEPARTMENTS_ABOVE_AVERAGE_SQL = text("""
    WITH dept_hires AS (
        SELECT
            d.id,
            d.department,
            COUNT(he.id) AS hired
        FROM departments d
        LEFT JOIN hired_employees he
            ON he.department_id = d.id
            AND EXTRACT(YEAR FROM he.datetime) = :year
        GROUP BY d.id, d.department
    )
    SELECT id, department, hired
    FROM dept_hires
    WHERE hired > (SELECT AVG(hired) FROM dept_hires)
    ORDER BY hired DESC
""")


def get_hires_by_quarter(db: Session, year: int = 2021) -> list[HiresByQuarterRow]:
    rows = db.execute(_HIRES_BY_QUARTER_SQL, {"year": year}).mappings().all()
    return [
        HiresByQuarterRow(
            department=row["department"],
            job=row["job"],
            Q1=row["q1"],
            Q2=row["q2"],
            Q3=row["q3"],
            Q4=row["q4"],
        )
        for row in rows
    ]


def get_departments_above_average(db: Session, year: int = 2021) -> list[DepartmentAboveAverageRow]:
    rows = db.execute(_DEPARTMENTS_ABOVE_AVERAGE_SQL, {"year": year}).mappings().all()
    return [
        DepartmentAboveAverageRow(id=row["id"], department=row["department"], hired=row["hired"])
        for row in rows
    ]
