from pydantic import BaseModel, computed_field
from core.models.folder import Folder
from core.models.document import Document

class DocumentTree(BaseModel):
    data: Folder | Document
    children: list["DocumentTree"] = []

    @computed_field
    @property
    def type(self) -> str:
        return type(self.data).__name__
