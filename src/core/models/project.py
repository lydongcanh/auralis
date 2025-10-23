from pydantic import BaseModel
from core.models.base_entity import BaseEntity

class Project(BaseEntity):
    id: str
    name: str
    description: str | None
    data_room_ids: list[str]
    accessible_user_project_ids: list[str]

class ProjectIn(BaseModel):
    name: str
    description: str | None
