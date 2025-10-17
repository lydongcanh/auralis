from fastapi import FastAPI

from core.infrastructure.proxies.ansarada.ansarada_api import AnsaradaApi
from core.services.data_room_service import DataRoomService
from core.models.data_room import DataRoom

app = FastAPI()


@app.get("/ansarada/data_rooms")
async def get_data_rooms(access_token: str, first: int = 10) -> list[DataRoom]:
    data_room_service = DataRoomService(AnsaradaApi())
    return await data_room_service.get_ansarada_data_rooms(access_token, first)