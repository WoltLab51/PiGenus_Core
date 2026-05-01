from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class Device(SQLModel, table=True):
    __tablename__ = "devices"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    hostname: str
    device_type: str
    owner_user_id: Optional[str] = Field(default=None)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    is_trusted: bool = Field(default=False)
