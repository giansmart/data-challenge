import json
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings


def log_rejected(table: str, row: dict, errors: list[str]) -> None:
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "table": table,
        "row": row,
        "errors": errors,
        "rejected_at": datetime.now(timezone.utc).isoformat(),
    }

    log_path = log_dir / f"rejected_{table}.log"
    with log_path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
