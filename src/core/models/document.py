from core.models.base_entity import BaseEntity

class Document(BaseEntity):
    name: str
    content: str
    data_room_id: str