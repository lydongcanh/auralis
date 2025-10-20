from pydantic import BaseModel
from core.models.base_entity import BaseEntity
from core.models.data_room_source import DataRoomSource

class DataRoom(BaseEntity):
    name: str
    source: DataRoomSource
    root_folder_id: str


class DataRoomIn(BaseModel):
    name: str
    source: DataRoomSource