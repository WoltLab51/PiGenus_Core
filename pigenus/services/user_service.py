from typing import Optional
from sqlmodel import Session, select, func
from pigenus.models.user import User
from pigenus.security.hashing import hash_password, verify_password
import uuid
from datetime import datetime, timezone


def create_user(username: str, email: str, password: str, session: Session, is_admin: bool = False) -> User:
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=hash_password(password),
        is_admin=is_admin,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_username(username: str, session: Session) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def get_user_count(session: Session) -> int:
    statement = select(func.count()).select_from(User)
    return session.exec(statement).one()


def authenticate_user(username: str, password: str, session: Session) -> Optional[User]:
    user = get_user_by_username(username, session)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
