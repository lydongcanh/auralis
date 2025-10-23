from core.infrastructure.repositories.user_repository import UserRepository
from core.models.user import User, UserAccessibleProjectOut, UserIn

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user_async(self, user_data: UserIn) -> User | None:
        return await self.user_repository.create_user_async(user_data)
    
    async def get_user_async(self, user_id: str) -> User | None:
        return await self.user_repository.get_user_async(user_id)

    async def get_user_accessible_projects_async(self, user_id: str) -> list[UserAccessibleProjectOut]:
        return await self.user_repository.get_user_accessible_projects_async(user_id)
