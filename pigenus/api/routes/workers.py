from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session
from pydantic import BaseModel
from pigenus.security.dependencies import get_db, get_current_admin, get_worker_from_token
from pigenus.models.user import User
from pigenus.services.worker_service import register_worker, heartbeat
from pigenus.workers.coordinator import list_workers, get_worker
from pigenus.security.auth import create_worker_token

router = APIRouter(prefix="/workers", tags=["workers"])


class WorkerRegisterRequest(BaseModel):
    name: str
    hostname: str
    capabilities: List[str] = []
    secret: str


class WorkerHeartbeatRequest(BaseModel):
    status: str = "idle"


class WorkerResponse(BaseModel):
    id: str
    name: str
    hostname: str
    capabilities: str
    status: str
    worker_token: Optional[str] = None


@router.post("/register", response_model=WorkerResponse, status_code=201)
def register_worker_endpoint(data: WorkerRegisterRequest, session: Session = Depends(get_db)):
    worker = register_worker(data.name, data.hostname, data.capabilities, data.secret, session)
    token = create_worker_token(worker.id, worker.name)
    return WorkerResponse(id=worker.id, name=worker.name, hostname=worker.hostname,
                           capabilities=worker.capabilities, status=worker.status, worker_token=token)


@router.post("/{worker_id}/heartbeat")
def worker_heartbeat(
    worker_id: str,
    data: WorkerHeartbeatRequest,
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_db),
):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        worker = get_worker_from_token(token, session)
        if worker.id != worker_id:
            raise HTTPException(status_code=403, detail="Token does not match worker_id")
    worker = heartbeat(worker_id, data.status, session)
    return {"id": worker.id, "status": worker.status, "last_heartbeat": worker.last_heartbeat}


@router.get("", response_model=List[WorkerResponse])
def list_all_workers(
    admin: User = Depends(get_current_admin),
    session: Session = Depends(get_db),
):
    workers = list_workers(session)
    return [WorkerResponse(id=w.id, name=w.name, hostname=w.hostname,
                            capabilities=w.capabilities, status=w.status) for w in workers]


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker_detail(worker_id: str, session: Session = Depends(get_db)):
    worker = get_worker(worker_id, session)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return WorkerResponse(id=worker.id, name=worker.name, hostname=worker.hostname,
                           capabilities=worker.capabilities, status=worker.status)
