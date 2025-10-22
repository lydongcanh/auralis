from core.infrastructure.repositories.project_repository import ProjectRepository
from core.models.project import Project, ProjectIn
from core.models.user_project import UserProjectIn

class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.project_repository = project_repository

    async def create_project_async(self, project: ProjectIn) -> Project:
        return await self.project_repository.create_project_async(project)

    async def link_data_room_to_project_async(self, data_room_id: str, project_id: str) -> None:
        await self.project_repository.link_data_room_to_project_async(data_room_id, project_id)

    async def unlink_data_room_from_project_async(self, data_room_id: str, project_id: str) -> None:
        await self.project_repository.unlink_data_room_from_project_async(data_room_id, project_id)

    async def add_user_to_project_async(self, user_project: UserProjectIn) -> None:
        await self.project_repository.add_user_to_project_async(user_project)

    async def remove_user_from_project_async(self, user_id: str, project_id: str) -> None:
        await self.project_repository.remove_user_from_project_async(user_id, project_id)

    async def get_project_by_id_async(self, project_id: str) -> Project | None:
        return await self.project_repository.get_project_by_id_async(project_id)
