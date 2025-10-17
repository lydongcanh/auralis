from datetime import datetime
from uuid import uuid4
from core.models.entity_status import EntityStatus
from core.models.project import Project


class ProjectService:
    async def create_project_async(self, name: str, description: str) -> Project:
        return Project(
            id=uuid4().hex,
            name=name,
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=EntityStatus.ACTIVE,
            data_rooms=[]
        )
    
    async def get_project_by_id_async(self, project_id: str) -> Project:
        return Project(
            id=project_id,
            name="Sample Project",
            description="This is a sample project.",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status=EntityStatus.ACTIVE,
            data_rooms=[]
        )
    
    async def get_projects_async(self) -> list[Project]:
        return [
            Project(
                id=str(i),
                name=f"Sample Project {i}",
                description="This is a sample project.",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status=EntityStatus.ACTIVE,
                data_rooms=[]
            )
            for i in range(5)
        ]
    
    async def link_data_room_to_project_async(self, project_id: str, data_room_id: str) -> None:
        # This is a placeholder implementation.
        pass