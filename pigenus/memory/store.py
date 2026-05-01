import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from pigenus.models.memory import MemoryItem


def store_memory(
    key: str,
    content: str,
    content_type: str = "text",
    tags: Optional[list] = None,
    source: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    importance_score: float = 0.0,
    *,
    session: Session,
) -> MemoryItem:
    existing = session.exec(select(MemoryItem).where(MemoryItem.key == key)).first()
    if existing:
        existing.content = content
        existing.content_type = content_type
        existing.tags_json = json.dumps(tags) if tags else None
        existing.source = source
        existing.expires_at = expires_at
        existing.importance_score = importance_score
        existing.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    item = MemoryItem(
        id=str(uuid.uuid4()),
        key=key,
        content=content,
        content_type=content_type,
        tags_json=json.dumps(tags) if tags else None,
        source=source,
        expires_at=expires_at,
        importance_score=importance_score,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_memory(key: str, session: Session) -> Optional[MemoryItem]:
    return session.exec(select(MemoryItem).where(MemoryItem.key == key)).first()


def list_memory(
    search: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50,
    *,
    session: Session,
) -> list[MemoryItem]:
    statement = select(MemoryItem)
    items = list(session.exec(statement).all())
    if search:
        items = [i for i in items if search.lower() in i.content.lower() or search.lower() in i.key.lower()]
    if tag:
        filtered = []
        for i in items:
            if i.tags_json:
                tags = json.loads(i.tags_json)
                if tag in tags:
                    filtered.append(i)
        items = filtered
    return items[:limit]


def delete_memory(key: str, session: Session) -> bool:
    item = get_memory(key, session)
    if not item:
        return False
    session.delete(item)
    session.commit()
    return True
