from typing import Optional
from core.infrastructure.database.database_client import DatabaseClient
from core.models.project import Project, ProjectIn
from core.models.entity_status import EntityStatus

class ProjectRepository:
    def __init__(self, database_client: DatabaseClient):
        self.db = database_client

    async def create_project_async(self, project: ProjectIn) -> Project:
        sql = "INSERT INTO projects (name, description) VALUES (:name, :description) RETURNING id, created_at, updated_at"
        result = (await self.db.execute_sql_async(sql, {"name": project.name, "description": project.description}))[0]
        
        return Project(
            id=str(result["id"]),
            name=project.name,
            description=project.description,
            data_room_ids=[],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            status=EntityStatus.ACTIVE,
            accessible_user_project_ids=[]
        )

    async def get_project_by_id_async(self, project_id: str) -> Optional[Project]:
        sql = "SELECT * FROM projects WHERE id = :project_id"
        result = (await self.db.execute_sql_async(sql, {"project_id": project_id}))[0]

        if result:
            return Project(
                id=str(result["id"]),
                name=result["name"],
                description=result["description"],
                data_room_ids=[],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
                status=EntityStatus.ACTIVE,
                accessible_user_project_ids=[]
            )
        
        return None
