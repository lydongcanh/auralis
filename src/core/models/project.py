from typing import Optional
from core.models.base_entity import BaseEntity
from core.models.data_room import DataRoom

class Project(BaseEntity):
    id: str
    name: str
    description: Optional[str]
    data_rooms: list[DataRoom]
    
