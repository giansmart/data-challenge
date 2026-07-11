import logging

from app.db import engine
from app.logging_config import setup_logging
from app.models import Base

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created (or already present) on %r", engine.url.database)


if __name__ == "__main__":
    main()
