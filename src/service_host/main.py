from fastapi import FastAPI, Body, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.infrastructure.proxies.ansarada.ansarada_api import AnsaradaApi
from core.infrastructure.database.database_client import DatabaseClient
from core.infrastructure.repositories.data_room_repository import DataRoomRepository
from core.infrastructure.repositories.project_repository import ProjectRepository
from core.infrastructure.repositories.user_repository import UserRepository
from core.services.project_service import ProjectService
from core.services.data_room_service import DataRoomService
from core.services.user_service import UserService
from core.models.data_room import DataRoom, DataRoomIn
from core.models.project import Project, ProjectIn
from core.models.user import User, UserAccessibleProjectOut, UserIn
from core.models.user_project import UserProjectIn
from core.models.user_role import UserRole

load_dotenv()

database_client = DatabaseClient()
data_room_service = DataRoomService(DataRoomRepository(database_client), AnsaradaApi())
project_service = ProjectService(ProjectRepository(database_client))
user_service = UserService(UserRepository(database_client))

app = FastAPI()

# CORS
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/projects/{project_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_user_to_project_async(project_id: str, user_id: str, user_role: UserRole = Body(..., embed=True)) -> None:
    user_project = UserProjectIn(project_id=project_id, user_id=user_id, user_role=user_role)
    return await project_service.add_user_to_project_async(user_project)

@app.delete("/projects/{project_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_project_async(project_id: str, user_id: str) -> None:
    await project_service.remove_user_from_project_async(user_id, project_id)

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


# Users
@app.post("/users")
async def create_user_async(user: UserIn) -> User | None:
    return await user_service.create_user_async(user)

@app.get("/users/{user_id}")
async def get_user_by_id_async(user_id: str) -> User | None:
    return await user_service.get_user_async(user_id)

@app.get("/users/{user_id}/projects")
async def get_user_accessible_projects_async(user_id: str) -> list[UserAccessibleProjectOut]:
    return await user_service.get_user_accessible_projects_async(user_id)
