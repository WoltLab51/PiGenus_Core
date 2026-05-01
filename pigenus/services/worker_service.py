import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlmodel import Session, select
from pigenus.models.worker import Worker
from pigenus.security.hashing import hash_secret
from pigenus.core.config import get_settings


def register_worker(name: str, hostname: str, capabilities: list, secret: str, session: Session) -> Worker:
    worker = Worker(
        id=str(uuid.uuid4()),
        name=name,
        hostname=hostname,
        capabilities=json.dumps(capabilities),
        status="idle",
        last_heartbeat=datetime.now(timezone.utc).replace(tzinfo=None),
        registered_at=datetime.now(timezone.utc).replace(tzinfo=None),
        secret_hash=hash_secret(secret),
    )
    session.add(worker)
    session.commit()
    session.refresh(worker)
    return worker


def heartbeat(worker_id: str, status: str, session: Session) -> Worker:
    worker = session.get(Worker, worker_id)
    if not worker:
        raise ValueError(f"Worker {worker_id} not found")
    worker.last_heartbeat = datetime.now(timezone.utc).replace(tzinfo=None)
    worker.status = status
    session.add(worker)
    session.commit()
    session.refresh(worker)
    return worker


def mark_offline_workers(session: Session) -> int:
    settings = get_settings()
    threshold = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=settings.worker_heartbeat_timeout_seconds)
    statement = select(Worker).where(Worker.last_heartbeat < threshold, Worker.status != "offline")
    workers = session.exec(statement).all()
    count = 0
    for worker in workers:
        worker.status = "offline"
        session.add(worker)
        count += 1
    session.commit()
    return count
