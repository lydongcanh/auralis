from datetime import datetime
from core.infrastructure.proxies.ansarada.ansarada_api import AnsaradaApi
from core.models.data_room import DataRoom
from core.models.data_room_source import DataRoomSource
from core.models.entity_status import EntityStatus


class DataRoomService:
    def __init__(self, ansarada_api: AnsaradaApi):
        self.ansarada_api = ansarada_api

    async def get_ansarada_data_rooms_async(self, access_token: str, first: int = 10) -> list[DataRoom]:
        response = await self.ansarada_api.get_data_rooms_async(access_token, first)

        data_rooms = []
        data_room_users = response["me"]["dataRoomUsers"]["nodes"]
        for data_room_user in data_room_users:
            data_room = data_room_user["dataRoom"]
            data_rooms.append(DataRoom(
                id=f"{DataRoomSource.Ansarada.value}_{data_room['id']}",
                name=data_room["displayName"], 
                created_at=datetime.now(), 
                updated_at=datetime.now(), 
                source=DataRoomSource.Ansarada,
                status=EntityStatus.ACTIVE
            ))

        return data_rooms
