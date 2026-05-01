from pigenus.db.base import create_db_and_tables
from pigenus.core.logging import get_logger

logger = get_logger(__name__)


def init_db():
    logger.info("Initializing database...")
    create_db_and_tables()
    logger.info("Database initialized.")
