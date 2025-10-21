from pydantic import BaseModel
from core.models.base_entity import BaseEntity

class User(BaseEntity):
    auth_provider_user_id: str
    accessible_user_project_ids: list[str]

class UserIn(BaseModel):
    auth_provider_user_id: str
