import json
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select, col
from pigenus.models.job import Job, JobEvent
from pigenus.core.config import get_settings


def submit_job(payload, session: Session) -> Job:
    job = Job(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=getattr(payload, "description", None),
        job_type=payload.job_type,
        payload_json=getattr(payload, "payload_json", None),
        status="pending",
        priority=getattr(payload, "priority", 0),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by_user_id=getattr(payload, "created_by_user_id", None),
    )
    session.add(job)
    _add_event(job.id, "submitted", session)
    session.commit()
    session.refresh(job)
    return job


def lease_job(worker_id: str, capabilities: list, session: Session) -> Optional[Job]:
    statement = (
        select(Job)
        .where(Job.status == "pending")
        .order_by(col(Job.priority).desc(), col(Job.created_at).asc())
    )
    jobs = session.exec(statement).all()
    for job in jobs:
        if job.payload_json:
            try:
                p = json.loads(job.payload_json)
                required_caps = p.get("required_capabilities", [])
                if required_caps and not set(required_caps).issubset(set(capabilities)):
                    continue
            except (json.JSONDecodeError, AttributeError):
                pass
        job.status = "leased"
        job.worker_id = worker_id
        job.leased_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        session.add(job)
        _add_event(job.id, "leased", session, worker_id=worker_id)
        session.commit()
        session.refresh(job)
        return job
    return None


def ack_job(job_id: str, worker_id: str, session: Session) -> Job:
    job = session.get(Job, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")
    job.status = "running"
    job.updated_at = datetime.utcnow()
    session.add(job)
    _add_event(job_id, "ack", session, worker_id=worker_id)
    session.commit()
    session.refresh(job)
    return job


def complete_job(job_id: str, worker_id: str, result: Optional[dict], session: Session) -> Job:
    job = session.get(Job, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")
    job.status = "completed"
    job.completed_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()
    job.result_json = json.dumps(result) if result else None
    session.add(job)
    _add_event(job_id, "completed", session, worker_id=worker_id)
    session.commit()
    session.refresh(job)
    return job


def fail_job(job_id: str, worker_id: str, error: str, session: Session) -> Job:
    job = session.get(Job, job_id)
    if not job:
        raise ValueError(f"Job {job_id} not found")
    job.status = "failed"
    job.error_message = error
    job.completed_at = datetime.utcnow()
    job.updated_at = datetime.utcnow()
    session.add(job)
    _add_event(job_id, "failed", session, worker_id=worker_id, message=error)
    session.commit()
    session.refresh(job)
    return job


def requeue_stuck_jobs(session: Session) -> int:
    settings = get_settings()
    threshold = datetime.utcnow() - timedelta(seconds=settings.job_lease_timeout_seconds)
    statement = select(Job).where(
        col(Job.status).in_(["leased", "running"]),
        col(Job.updated_at) < threshold,
    )
    jobs = session.exec(statement).all()
    count = 0
    for job in jobs:
        job.status = "pending"
        job.worker_id = None
        job.leased_at = None
        job.updated_at = datetime.utcnow()
        session.add(job)
        _add_event(job.id, "requeued", session, message="Stuck job requeued")
        count += 1
    session.commit()
    return count


def _add_event(job_id: str, event_type: str, session: Session,
               worker_id: Optional[str] = None, message: Optional[str] = None) -> None:
    event = JobEvent(
        id=str(uuid.uuid4()),
        job_id=job_id,
        event_type=event_type,
        timestamp=datetime.utcnow(),
        worker_id=worker_id,
        message=message,
    )
    session.add(event)
