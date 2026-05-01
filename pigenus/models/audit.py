from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None), index=True)
    actor_type: str
    actor_id: Optional[str] = Field(default=None)
    action: str
    resource_type: Optional[str] = Field(default=None)
    resource_id: Optional[str] = Field(default=None)
    details_json: Optional[str] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)
