from fastapi import FastAPI
from dotenv import load_dotenv

from core.infrastructure.proxies.ansarada.ansarada_api import AnsaradaApi
from core.infrastructure.database.database_client import DatabaseClient
from core.infrastructure.repositories.project_repository import ProjectRepository
from core.services.project_service import ProjectService
from core.services.data_room_service import DataRoomService
from core.models.data_room import DataRoom
from core.models.project import Project, ProjectIn


load_dotenv()

database_client = DatabaseClient()
data_room_service = DataRoomService(AnsaradaApi())
project_service = ProjectService(project_repository=ProjectRepository(database_client))

app = FastAPI()

# Projects
@app.post("/projects")
async def create_project_async(project: ProjectIn) -> Project:
    return await project_service.create_project_async(project)

@app.get("/projects/{project_id}")
async def get_project_by_id_async(project_id: str) -> Project | None:
    return await project_service.get_project_by_id_async(project_id)


# Data Rooms
@app.get("/ansarada/data_rooms")
async def get_ansarada_data_rooms_async(access_token: str, first: int = 10) -> list[DataRoom]:
    return await data_room_service.get_ansarada_data_rooms_async(access_token, first)