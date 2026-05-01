from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pigenus.security.dependencies import get_db, require_admin_token
from pigenus.models.audit import AuditLog
from pigenus.models.worker import Worker
from pigenus.monitoring.health import get_health_status
from pigenus.monitoring.metrics import get_metrics
from pigenus.services.job_service import requeue_stuck_jobs

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status")
def system_status(
    _: None = Depends(require_admin_token),
    session: Session = Depends(get_db),
):
    health = get_health_status(session)
    metrics = get_metrics(session)
    return {"health": health, "metrics": metrics}


@router.get("/audit-log")
def audit_log(
    limit: int = 50,
    _: None = Depends(require_admin_token),
    session: Session = Depends(get_db),
):
    statement = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    logs = session.exec(statement).all()
    return {"logs": [{"id": l.id, "timestamp": str(l.timestamp), "actor_type": l.actor_type,
                       "action": l.action, "resource_type": l.resource_type} for l in logs]}


@router.get("/workers/status")
def workers_status(
    _: None = Depends(require_admin_token),
    session: Session = Depends(get_db),
):
    workers = session.exec(select(Worker)).all()
    summary = {
        "total": len(workers),
        "idle": sum(1 for w in workers if w.status == "idle"),
        "busy": sum(1 for w in workers if w.status == "busy"),
        "offline": sum(1 for w in workers if w.status == "offline"),
    }
    return summary


@router.post("/jobs/requeue-stuck")
def requeue_stuck(
    _: None = Depends(require_admin_token),
    session: Session = Depends(get_db),
):
    count = requeue_stuck_jobs(session)
    return {"requeued": count}
