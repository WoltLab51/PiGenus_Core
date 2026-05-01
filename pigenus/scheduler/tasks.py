import logging
import shutil
from datetime import datetime
from pigenus.core.config import get_settings

logger = logging.getLogger(__name__)


def rotate_logs() -> None:
    logger.info("Log rotation triggered at %s", datetime.utcnow().isoformat())


def create_backup() -> None:
    settings = get_settings()
    if settings.database_url.startswith("sqlite:///"):
        db_path = settings.database_url.replace("sqlite:///", "")
        backup_path = db_path + f".backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(db_path, backup_path)
            logger.info("Database backup created at %s", backup_path)
        except Exception as e:
            logger.warning("Backup failed: %s", e)
    else:
        logger.info("Non-file SQLite DB, skipping backup.")


def summarize_sessions() -> None:
    logger.info("Session summary: placeholder - no stats computed")


def requeue_stuck_jobs() -> None:
    from pigenus.db.base import get_session
    from pigenus.services.job_service import requeue_stuck_jobs as _requeue
    session = next(get_session())
    try:
        count = _requeue(session)
        logger.info("Requeued %d stuck jobs", count)
    finally:
        session.close()


def mark_offline_workers() -> None:
    from pigenus.db.base import get_session
    from pigenus.services.worker_service import mark_offline_workers as _mark
    session = next(get_session())
    try:
        count = _mark(session)
        logger.info("Marked %d workers as offline", count)
    finally:
        session.close()


def prepare_daily_briefing() -> None:
    from pigenus.db.base import get_session
    from pigenus.monitoring.metrics import get_metrics
    session = next(get_session())
    try:
        metrics = get_metrics(session)
        logger.info("Daily briefing: %s", metrics)
    finally:
        session.close()
