from core.infrastructure.database.database_client import DatabaseClient
from core.models.entity_status import EntityStatus
from core.models.user import User, UserAccessibleProjectOut, UserIn

class UserRepository:
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client

    async def create_user_async(self, user: UserIn) -> User | None:
        sql = '''
            INSERT INTO users (auth_provider_user_id) 
            VALUES (:auth_provider_user_id)
            RETURNING id, created_at, updated_at
        '''
        result = (await self.db_client.execute_sql_async(sql, {"auth_provider_user_id": user.auth_provider_user_id}))[0]

        if not result:
            return None
        
        return User(
            id=str(result["id"]),
            auth_provider_user_id=user.auth_provider_user_id,
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            status=EntityStatus.ACTIVE,
            accessible_user_project_ids=[]
        )
    
    async def get_user_async(self, user_id: str) -> User | None:
        sql = "SELECT * FROM users WHERE id = :id"
        result = (await self.db_client.execute_sql_async(sql, {"id": user_id}))[0]

        if not result:
            return None
        
        return User(
            id=str(result["id"]),
            auth_provider_user_id=result["auth_provider_user_id"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            status=EntityStatus.ACTIVE,
            accessible_user_project_ids=[]
        )

    async def get_user_accessible_projects_async(self, user_id: str) -> list[UserAccessibleProjectOut]:
        sql = '''
            SELECT p.id, p.name, p.description, p.created_at, p.updated_at, p.status, up.user_role
            FROM projects p
                JOIN user_projects up ON p.id = up.project_id
            WHERE up.user_id = :user_id
        '''
        results = await self.db_client.execute_sql_async(sql, {"user_id": user_id})

        if not results:
            return []

        return [UserAccessibleProjectOut(
            id=str(result["id"]),
            name=result["name"],
            description=result["description"],
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            role=result["user_role"],
            status=result["status"]
        ) for result in results]