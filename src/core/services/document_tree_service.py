from core.infrastructure.repositories.document_tree_repository import DocumentTreeRepository
from core.models.folder import Folder, FolderIn
from core.models.document import Document, DocumentIn
from core.models.document_tree import DocumentTree


class DocumentTreeService:
    def __init__(self, document_tree_repository: DocumentTreeRepository):
        self.document_tree_repository = document_tree_repository

    async def create_folder_async(self, folder: FolderIn) -> Folder | None:
        return await self.document_tree_repository.create_folder_async(folder)

    async def create_document_async(self, document: DocumentIn) -> Document | None:
        return await self.document_tree_repository.create_document_async(document)

    async def get_document_tree_async(self, data_room_id: str) -> DocumentTree | None:
        return await self.document_tree_repository.get_document_tree_async(data_room_id)
