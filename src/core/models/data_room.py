from pydantic import BaseModel
from core.models.base_entity import BaseEntity
from core.models.data_room_source import DataRoomSource

class DataRoom(BaseEntity):
    name: str
    source: DataRoomSource
    root_folder_id: str

    # Only available for Ansarada sources
    client_id: str | None
    client_secret: str | None


class DataRoomIn(BaseModel):
    name: str
    source: DataRoomSource
    client_id: str | None = None
    client_secret: str | None = None