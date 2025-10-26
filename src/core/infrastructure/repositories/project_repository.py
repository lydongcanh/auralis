from typing import Optional
from core.infrastructure.database.database_client import DatabaseClient
from core.models.project import Project, ProjectIn, ProjectUserOut
from core.models.data_room import DataRoom
from core.models.user import User, UserAccessibleProjectOut
from core.models.user_project import UserProjectIn
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

    async def link_data_room_to_project_async(self, data_room_id: str, project_id: str) -> None:
        sql = '''
            INSERT INTO project_data_rooms (project_id, data_room_id)
            VALUES (:project_id, :data_room_id)
        '''
        await self.db.execute_sql_async(sql, {"project_id": project_id, "data_room_id": data_room_id})
        
    async def unlink_data_room_from_project_async(self, data_room_id: str, project_id: str) -> None:
        sql = '''
            DELETE FROM project_data_rooms
            WHERE project_id = :project_id AND data_room_id = :data_room_id
        '''
        await self.db.execute_sql_async(sql, {"project_id": project_id, "data_room_id": data_room_id})

    async def add_user_to_project_async(self, user_project: UserProjectIn) -> None:
        sql = '''
            INSERT INTO user_projects (project_id, user_id, user_role)
            VALUES (:project_id, :user_id, :user_role)
        '''
        params = {
            "project_id": user_project.project_id, 
            "user_id": user_project.user_id, 
            "user_role": user_project.user_role.value
        }
        await self.db.execute_sql_async(sql, params)

    async def remove_user_from_project_async(self, user_id: str, project_id: str) -> None:
        sql = '''
            DELETE FROM user_projects
            WHERE project_id = :project_id AND user_id = :user_id
        '''
        await self.db.execute_sql_async(sql, {"project_id": project_id, "user_id": user_id})

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

    async def get_project_data_rooms_async(self, project_id: str) -> list[DataRoom]:
        sql = '''
            SELECT dr.* FROM data_rooms dr
            JOIN project_data_rooms pdr ON dr.id = pdr.data_room_id
            WHERE pdr.project_id = :project_id
        '''
        results = await self.db.execute_sql_async(sql, {"project_id": project_id})
        if not results:
            return []
        
        return [DataRoom(
            id=str(data_room["id"]),
            name=data_room["name"],
            source=data_room["source"],
            created_at=data_room["created_at"],
            updated_at=data_room["updated_at"],
            status=data_room["status"],
            root_folder_id=str(data_room["root_folder_id"]),
        ) for data_room in results]

    async def get_project_users_async(self, project_id: str) -> list[ProjectUserOut]:
        sql = '''
            SELECT u.id, u.auth_provider_user_id, up.user_role
            FROM users u
                JOIN user_projects up ON u.id = up.user_id
            WHERE up.project_id = :project_id
        '''
        results = await self.db.execute_sql_async(sql, {"project_id": project_id})
        
        if not results:
            return []

        return [ProjectUserOut(
            user_id=str(result["id"]),
            user_auth_provider_user_id=result["auth_provider_user_id"],
            user_role=result["user_role"]
        ) for result in results]
