from typing import Optional
from sqlmodel import Session, select
from pigenus.models.worker import Worker


def get_worker(worker_id: str, session: Session) -> Optional[Worker]:
    return session.get(Worker, worker_id)


def list_workers(session: Session) -> list[Worker]:
    statement = select(Worker)
    return list(session.exec(statement).all())


def update_worker_status(worker_id: str, status: str, session: Session) -> Optional[Worker]:
    worker = session.get(Worker, worker_id)
    if not worker:
        return None
    worker.status = status
    session.add(worker)
    session.commit()
    session.refresh(worker)
    return worker
