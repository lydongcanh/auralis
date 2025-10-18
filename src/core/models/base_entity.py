from pydantic import BaseModel
from datetime import datetime
from core.models.entity_status import EntityStatus

class BaseEntity(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    status: EntityStatus