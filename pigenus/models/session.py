from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class UserSession(SQLModel, table=True):
    __tablename__ = "user_sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    token_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    expires_at: datetime
    is_active: bool = Field(default=True)
    device_id: Optional[str] = Field(default=None)
