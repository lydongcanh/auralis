from pydantic import BaseModel
from core.models.base_entity import BaseEntity

class Folder(BaseEntity):
    name: str
    data_room_id: str
    parent_folder_id: str | None
    children_folder_ids: list[str]
    document_ids: list[str]

    @property
    def is_root(self):
        return self.parent_folder_id is None

    @property
    def has_children_folders(self):
        return len(self.children_folder_ids) > 0

    @property
    def has_documents(self):
        return len(self.document_ids) > 0
    
    @property
    def is_empty(self):
        return not self.has_children_folders and not self.has_documents
    
class FolderIn(BaseModel):
    name: str
    data_room_id: str
    parent_folder_id: str
