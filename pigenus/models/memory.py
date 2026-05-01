from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class MemoryItem(SQLModel, table=True):
    __tablename__ = "memory_items"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    key: str = Field(index=True, unique=True)
    content: str
    content_type: str = Field(default="text")
    tags_json: Optional[str] = Field(default=None)
    source: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    expires_at: Optional[datetime] = Field(default=None)
    importance_score: float = Field(default=0.0)
