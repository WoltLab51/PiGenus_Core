import json
import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import Session
from pigenus.models.audit import AuditLog


def log_event(
    actor_type: str,
    action: str,
    session: Session,
    actor_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip: Optional[str] = None,
) -> AuditLog:
    log = AuditLog(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details_json=json.dumps(details) if details else None,
        ip_address=ip,
    )
    session.add(log)
    session.commit()
    return log
