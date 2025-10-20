from datetime import datetime
from core.infrastructure.proxies.ansarada.ansarada_api import AnsaradaApi
from core.infrastructure.repositories.data_room_repository import DataRoomRepository
from core.models.data_room import DataRoom, DataRoomIn
from core.models.data_room_source import DataRoomSource
from core.models.entity_status import EntityStatus


class DataRoomService:
    def __init__(self, data_room_repository: DataRoomRepository, ansarada_api: AnsaradaApi):
        self.data_room_repository = data_room_repository
        self.ansarada_api = ansarada_api

    async def create_data_room_with_root_folder_async(self, data_room: DataRoomIn) -> DataRoom:
        return await self.data_room_repository.create_data_room_with_root_folder_async(data_room)

    async def get_data_room_by_id_async(self, id: str) -> DataRoom | None:
        return await self.data_room_repository.get_data_room_by_id_async(id)

    async def get_ansarada_data_rooms_async(self, access_token: str, first: int = 10) -> list[DataRoom]:
        response = await self.ansarada_api.get_data_rooms_async(access_token, first)

        data_rooms = []
        data_room_users = response["me"]["dataRoomUsers"]["nodes"]
        for data_room_user in data_room_users:
            data_room = data_room_user["dataRoom"]
            data_rooms.append(DataRoom(
                id=f"{DataRoomSource.ANSARADA.value}_{data_room['id']}",
                name=data_room["displayName"], 
                created_at=datetime.now(), 
                updated_at=datetime.now(), 
                source=DataRoomSource.ANSARADA,
                status=EntityStatus.ACTIVE,
                root_folder_id="",
            ))

        return data_rooms
