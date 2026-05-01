from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select
from pydantic import BaseModel
from pigenus.security.dependencies import get_db, get_current_user, get_current_admin, get_worker_from_token
from pigenus.models.user import User
from pigenus.models.job import Job
from pigenus.services.job_service import (
    submit_job, lease_job, ack_job, complete_job, fail_job, requeue_stuck_jobs
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobSubmitRequest(BaseModel):
    title: str
    job_type: str
    description: Optional[str] = None
    payload_json: Optional[str] = None
    priority: int = 0


class JobLeaseRequest(BaseModel):
    capabilities: List[str] = []


class JobCompleteRequest(BaseModel):
    result: Optional[dict] = None


class JobFailRequest(BaseModel):
    error: str


class JobResponse(BaseModel):
    id: str
    title: str
    job_type: str
    status: str
    priority: int
    worker_id: Optional[str] = None
    description: Optional[str] = None
    error_message: Optional[str] = None
    result_json: Optional[str] = None


@router.post("", response_model=JobResponse, status_code=201)
def submit_job_endpoint(
    data: JobSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    job = submit_job(
        title=data.title,
        job_type=data.job_type,
        description=data.description,
        payload_json=data.payload_json,
        priority=data.priority,
        created_by_user_id=current_user.id,
        session=session,
    )
    return _to_response(job)


@router.get("", response_model=List[JobResponse])
def list_jobs(
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    statement = select(Job)
    if status:
        statement = statement.where(Job.status == status)
    if job_type:
        statement = statement.where(Job.job_type == job_type)
    jobs = session.exec(statement).all()
    return [_to_response(j) for j in jobs]


@router.post("/lease")
def lease_job_endpoint(
    data: JobLeaseRequest,
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Worker token required")
    token = authorization.replace("Bearer ", "")
    worker = get_worker_from_token(token, session)
    if worker.status == "offline":
        raise HTTPException(status_code=403, detail="Worker is offline")
    job = lease_job(worker.id, data.capabilities, session)
    if not job:
        return {"job": None, "message": "No jobs available"}
    return {"job": _to_response(job)}


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_response(job)


@router.post("/{job_id}/ack")
def ack_job_endpoint(
    job_id: str,
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Worker token required")
    token = authorization.replace("Bearer ", "")
    worker = get_worker_from_token(token, session)
    try:
        job = ack_job(job_id, worker.id, session)
        return _to_response(job)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{job_id}/complete")
def complete_job_endpoint(
    job_id: str,
    data: JobCompleteRequest,
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Worker token required")
    token = authorization.replace("Bearer ", "")
    worker = get_worker_from_token(token, session)
    try:
        job = complete_job(job_id, worker.id, data.result, session)
        return _to_response(job)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{job_id}/fail")
def fail_job_endpoint(
    job_id: str,
    data: JobFailRequest,
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Worker token required")
    token = authorization.replace("Bearer ", "")
    worker = get_worker_from_token(token, session)
    try:
        job = fail_job(job_id, worker.id, data.error, session)
        return _to_response(job)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{job_id}", status_code=204)
def cancel_job(job_id: str, admin: User = Depends(get_current_admin), session: Session = Depends(get_db)):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = "cancelled"
    session.add(job)
    session.commit()


def _to_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        title=job.title,
        job_type=job.job_type,
        status=job.status,
        priority=job.priority,
        worker_id=job.worker_id,
        description=job.description,
        error_message=job.error_message,
        result_json=job.result_json,
    )
