from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class Worker(SQLModel, table=True):
    __tablename__ = "workers"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True)
    hostname: str
    capabilities: str = Field(default="[]")
    status: str = Field(default="idle")
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    secret_hash: str
    current_job_id: Optional[str] = Field(default=None)
