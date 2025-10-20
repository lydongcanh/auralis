from fastapi import FastAPI, status
from dotenv import load_dotenv

from core.infrastructure.proxies.ansarada.ansarada_api import AnsaradaApi
from core.infrastructure.database.database_client import DatabaseClient
from core.infrastructure.repositories.data_room_repository import DataRoomRepository
from core.infrastructure.repositories.project_repository import ProjectRepository
from core.services.project_service import ProjectService
from core.services.data_room_service import DataRoomService
from core.models.data_room import DataRoom, DataRoomIn
from core.models.project import Project, ProjectIn


load_dotenv()

database_client = DatabaseClient()
data_room_service = DataRoomService(DataRoomRepository(database_client), ansarada_api=AnsaradaApi())
project_service = ProjectService(ProjectRepository(database_client))

app = FastAPI()

# Projects
@app.post("/projects")
async def create_project_async(project: ProjectIn) -> Project:
    return await project_service.create_project_async(project)

@app.post("/projects/{project_id}/data-rooms/{data_room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def link_data_room_to_project_async(project_id: str, data_room_id: str) -> None:
    return await project_service.link_data_room_to_project_async(data_room_id, project_id)

@app.delete("/projects/{project_id}/data-rooms/{data_room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_data_room_from_project_async(project_id: str, data_room_id: str) -> None:
    await project_service.unlink_data_room_from_project_async(data_room_id, project_id)

@app.get("/projects/{project_id}")
async def get_project_by_id_async(project_id: str) -> Project | None:
    return await project_service.get_project_by_id_async(project_id)


# Data Rooms
@app.post("/data-rooms")
async def create_data_room_with_root_folder_async(data_room: DataRoomIn) -> DataRoom:
    return await data_room_service.create_data_room_with_root_folder_async(data_room)

@app.get("/data-rooms/{data_room_id}")
async def get_data_room_by_id_async(data_room_id: str) -> DataRoom | None:
    return await data_room_service.get_data_room_by_id_async(data_room_id)

@app.get("/ansarada/data-rooms")
async def get_ansarada_data_rooms_async(access_token: str, first: int = 10) -> list[DataRoom]:
    return await data_room_service.get_ansarada_data_rooms_async(access_token, first)