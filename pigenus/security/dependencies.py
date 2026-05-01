from typing import Annotated, Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from pigenus.db.base import get_session
from pigenus.models.user import User
from pigenus.models.worker import Worker
from pigenus.security.auth import verify_token
from pigenus.core.config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    yield from get_session()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_db),
) -> User:
    payload = verify_token(token)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def get_worker_from_token(token: str, session: Session) -> Worker:
    payload = verify_token(token)
    if payload.get("type") != "worker":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a worker token")
    worker_id = payload.get("sub")
    if not worker_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid worker token")
    worker = session.get(Worker, worker_id)
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")
    return worker


def require_admin_token(x_admin_token: str = Header(...)) -> None:
    settings = get_settings()
    if x_admin_token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")
