from pydantic import BaseModel
from datetime import datetime

from core.models.data_room_source import DataRoomSource

class DataRoom(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    source: DataRoomSource