from typing import Optional
from core.models.base_entity import BaseEntity

class Project(BaseEntity):
    id: str
    name: str
    description: Optional[str]
    data_room_ids: list[str]
    accessible_user_project_ids: list[str]
    
