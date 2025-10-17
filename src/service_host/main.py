from fastapi import FastAPI

from core.infrastructure.proxies.ansarada.ansarada_api import AnsaradaApi
from core.services.project_service import ProjectService
from core.services.data_room_service import DataRoomService
from core.models.data_room import DataRoom
from core.models.project import Project


app = FastAPI()
data_room_service = DataRoomService(AnsaradaApi())
project_service = ProjectService()


# Projects
@app.get("/projects")
async def get_projects_async() -> list[Project]:
    return await project_service.get_projects_async()


@app.post("/projects")
async def create_project_async(name: str, description: str) -> Project:
    return await project_service.create_project_async(name, description)


@app.get("/projects/{project_id}")
async def get_project_async(project_id: str) -> Project:
    return await project_service.get_project_by_id_async(project_id)


# Data Rooms
@app.get("/ansarada/data_rooms")
async def get_ansarada_data_rooms_async(access_token: str, first: int = 10) -> list[DataRoom]:
    return await data_room_service.get_ansarada_data_rooms_async(access_token, first)