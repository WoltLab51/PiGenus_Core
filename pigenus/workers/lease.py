import json
from typing import Optional
from sqlmodel import Session
from pigenus.models.job import Job
from pigenus.services.job_service import lease_job


def request_lease(worker_id: str, worker_capabilities_json: str, session: Session) -> Optional[Job]:
    try:
        capabilities = json.loads(worker_capabilities_json)
    except (json.JSONDecodeError, TypeError):
        capabilities = []
    return lease_job(worker_id, capabilities, session)
