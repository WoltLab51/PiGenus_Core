from fastapi import APIRouter, Depends
from sqlmodel import Session
from pigenus.security.dependencies import get_db
from pigenus.monitoring.health import get_health_status, get_detailed_health

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check(session: Session = Depends(get_db)):
    return get_health_status(session)


@router.get("/detailed")
def detailed_health(session: Session = Depends(get_db)):
    return get_detailed_health(session)
