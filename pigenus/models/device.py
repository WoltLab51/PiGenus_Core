from datetime import datetime
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
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    is_trusted: bool = Field(default=False)
