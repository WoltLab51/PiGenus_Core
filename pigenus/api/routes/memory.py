from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
from pigenus.security.dependencies import get_db, get_current_user
from pigenus.models.user import User
from pigenus.memory.store import store_memory, get_memory, list_memory, delete_memory

router = APIRouter(prefix="/memory", tags=["memory"])


class MemoryStoreRequest(BaseModel):
    key: str
    content: str
    content_type: str = "text"
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    expires_at: Optional[datetime] = None
    importance_score: float = 0.0


class MemoryResponse(BaseModel):
    id: str
    key: str
    content: str
    content_type: str
    importance_score: float
    tags_json: Optional[str] = None
    source: Optional[str] = None


@router.post("", response_model=MemoryResponse, status_code=201)
def store_memory_endpoint(
    data: MemoryStoreRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    item = store_memory(
        key=data.key,
        content=data.content,
        content_type=data.content_type,
        tags=data.tags,
        source=data.source,
        expires_at=data.expires_at,
        importance_score=data.importance_score,
        session=session,
    )
    return _to_response(item)


@router.get("", response_model=List[MemoryResponse])
def list_memory_endpoint(
    search: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    items = list_memory(search=search, tag=tag, limit=limit, session=session)
    return [_to_response(i) for i in items]


@router.get("/{key}", response_model=MemoryResponse)
def get_memory_endpoint(key: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    item = get_memory(key, session)
    if not item:
        raise HTTPException(status_code=404, detail="Memory item not found")
    return _to_response(item)


@router.delete("/{key}", status_code=204)
def delete_memory_endpoint(key: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    deleted = delete_memory(key, session)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory item not found")


def _to_response(item):
    return MemoryResponse(
        id=item.id,
        key=item.key,
        content=item.content,
        content_type=item.content_type,
        importance_score=item.importance_score,
        tags_json=item.tags_json,
        source=item.source,
    )
