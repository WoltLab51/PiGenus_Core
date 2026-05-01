from sqlmodel import Session, select, func
from pigenus.models.job import Job
from pigenus.models.worker import Worker
from pigenus.models.memory import MemoryItem


def get_metrics(session: Session) -> dict:
    total_jobs = session.exec(select(func.count()).select_from(Job)).one()
    pending_jobs = session.exec(select(func.count()).select_from(Job).where(Job.status == "pending")).one()
    total_workers = session.exec(select(func.count()).select_from(Worker)).one()
    online_workers = session.exec(select(func.count()).select_from(Worker).where(Worker.status != "offline")).one()
    total_memory = session.exec(select(func.count()).select_from(MemoryItem)).one()
    return {
        "total_jobs": total_jobs,
        "pending_jobs": pending_jobs,
        "total_workers": total_workers,
        "online_workers": online_workers,
        "total_memory_items": total_memory,
    }
