from core.models.base_entity import BaseEntity
from core.models.user_role import UserRole

class UserProject(BaseEntity):
    user_id: str
    project_id: str
    user_role: UserRole