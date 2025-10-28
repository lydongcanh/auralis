from pydantic import BaseModel
from core.models.base_entity import BaseEntity
from core.models.entity_status import EntityStatus
from core.models.user_role import UserRole

class Project(BaseEntity):
    id: str
    name: str
    description: str | None
    data_room_ids: list[str]
    accessible_user_project_ids: list[str]

class ProjectIn(BaseModel):
    name: str
    description: str | None

class ProjectUserOut(BaseModel):
    user_id: str
    user_auth_provider_user_id: str
    user_role: UserRole
    user_status: EntityStatus
