from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    description: Optional[str] = Field(default=None)
    job_type: str
    payload_json: Optional[str] = Field(default=None)
    status: str = Field(default="pending")
    priority: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    leased_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    worker_id: Optional[str] = Field(default=None)
    created_by_user_id: Optional[str] = Field(default=None)
    result_json: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None)


class JobEvent(SQLModel, table=True):
    __tablename__ = "job_events"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    job_id: str = Field(index=True)
    event_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    worker_id: Optional[str] = Field(default=None)
    message: Optional[str] = Field(default=None)
    metadata_json: Optional[str] = Field(default=None)
