from pydantic import BaseModel
from datetime import datetime
from core.models.base_entity import BaseEntity
from core.models.entity_status import EntityStatus
from core.models.user_role import UserRole

class User(BaseEntity):
    auth_provider_user_id: str
    accessible_user_project_ids: list[str]

class UserIn(BaseModel):
    auth_provider_user_id: str

class UserAccessibleProjectOut(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    status: EntityStatus
    role: UserRole
