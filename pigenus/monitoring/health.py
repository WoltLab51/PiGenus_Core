from datetime import datetime
from sqlmodel import Session, text
from pigenus.core.config import get_settings

_start_time = datetime.utcnow()


def check_db_health(session: Session) -> bool:
    try:
        session.exec(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_health_status(session: Session) -> dict:
    settings = get_settings()
    db_ok = check_db_health(session)
    uptime_seconds = (datetime.utcnow() - _start_time).total_seconds()
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.version,
        "uptime_seconds": uptime_seconds,
        "database": "ok" if db_ok else "error",
    }


def get_detailed_health(session: Session) -> dict:
    basic = get_health_status(session)
    from pigenus.monitoring.metrics import get_metrics
    basic["metrics"] = get_metrics(session)
    return basic
