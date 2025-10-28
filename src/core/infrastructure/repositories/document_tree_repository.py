from core.infrastructure.database.database_client import DatabaseClient
from core.models.folder import Folder, FolderIn
from core.models.document import Document, DocumentIn
from core.models.document_tree import DocumentTree
from core.models.entity_status import EntityStatus


class DocumentTreeRepository:
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client

    async def create_folder_async(self, folder: FolderIn) -> Folder | None:
        sql = '''
            INSERT INTO folders (name, data_room_id, parent_folder_id) 
            VALUES (:name, :data_room_id, :parent_folder_id)
            RETURNING id, created_at, updated_at
        '''
        params = {
            "name": folder.name,
            "data_room_id": folder.data_room_id,
            "parent_folder_id": folder.parent_folder_id
        }
        result = (await self.db_client.execute_sql_async(sql, params))[0]

        if not result:
            return None
        
        return Folder(
            id=str(result["id"]),
            name=folder.name,
            data_room_id=folder.data_room_id,
            parent_folder_id=folder.parent_folder_id,
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            status=EntityStatus.ACTIVE,
            children_folder_ids=[],
            document_ids=[]
        )

    async def create_document_async(self, document: DocumentIn) -> Document | None:
        sql = '''
            INSERT INTO documents (name, content, folder_id, data_room_id) 
            VALUES (:name, :content, :folder_id, :data_room_id)
            RETURNING id, created_at, updated_at
        '''
        params = {
            "name": document.name,
            "content": document.content,
            "folder_id": document.folder_id,
            "data_room_id": document.data_room_id
        }
        result = (await self.db_client.execute_sql_async(sql, params))[0]

        if not result:
            return None
        
        return Document(
            id=str(result["id"]),
            name=document.name,
            content=document.content,
            data_room_id=document.data_room_id,
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            status=EntityStatus.ACTIVE
        )
    
    async def get_document_tree_async(self, data_room_id: str) -> DocumentTree | None:
        sql = '''
            WITH RECURSIVE folder_tree AS (
                -- Base case: get the root folder
                SELECT 
                    f.id, f.name, f.data_room_id, f.parent_folder_id, 
                    f.created_at, f.updated_at, f.status,
                    0 as level, ARRAY[f.id] as path
                FROM data_rooms dr
                JOIN folders f ON dr.root_folder_id = f.id
                WHERE dr.id = :data_room_id AND dr.status = 'active' AND f.status = 'active'
                
                UNION ALL
                
                -- Recursive case: get child folders
                SELECT 
                    f.id, f.name, f.data_room_id, f.parent_folder_id,
                    f.created_at, f.updated_at, f.status,
                    ft.level + 1, ft.path || f.id
                FROM folders f
                JOIN folder_tree ft ON f.parent_folder_id = ft.id
                WHERE f.status = 'active'
            ),
            -- Get all documents for folders in the tree
            folder_documents AS (
                SELECT 
                    d.id, d.name, d.content, d.data_room_id, d.folder_id,
                    d.created_at, d.updated_at, d.status
                FROM documents d
                JOIN folder_tree ft ON d.folder_id = ft.id
                WHERE d.status = 'active'
            )
            -- Main query: get folders and documents together
            SELECT 
                'folder' as type,
                ft.id, ft.name, ft.data_room_id, ft.parent_folder_id,
                ft.created_at, ft.updated_at, ft.status, ft.level,
                NULL as content, NULL as folder_id
            FROM folder_tree ft
            
            UNION ALL
            
            SELECT 
                'document' as type,
                fd.id, fd.name, fd.data_room_id, NULL as parent_folder_id,
                fd.created_at, fd.updated_at, fd.status, NULL as level,
                fd.content, fd.folder_id
            FROM folder_documents fd
            
            ORDER BY type, level, name
        '''
        
        params = {"data_room_id": data_room_id}
        results = await self.db_client.execute_sql_async(sql, params)
        
        if not results:
            return None
        
        # Separate folders and documents
        folders_map = {}
        documents_by_folder = {}
        root_folder = None
        
        for row in results:
            if row["type"] == "folder":
                folder = Folder(
                    id=str(row["id"]),
                    name=row["name"],
                    data_room_id=str(row["data_room_id"]),
                    parent_folder_id=str(row["parent_folder_id"]) if row["parent_folder_id"] else None,
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    status=EntityStatus(row["status"]),
                    children_folder_ids=[],
                    document_ids=[]
                )
                folders_map[folder.id] = folder
                if folder.parent_folder_id is None:
                    root_folder = folder
            else:  # document
                document = Document(
                    id=str(row["id"]),
                    name=row["name"],
                    content=row["content"],
                    data_room_id=str(row["data_room_id"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    status=EntityStatus(row["status"])
                )
                folder_id = str(row["folder_id"])
                if folder_id not in documents_by_folder:
                    documents_by_folder[folder_id] = []
                documents_by_folder[folder_id].append(document)
        
        if not root_folder:
            return None
        
        # Build the tree structure
        def build_tree(folder: Folder) -> DocumentTree:
            # Find child folders
            child_folders = [f for f in folders_map.values() if f.parent_folder_id == folder.id]
            folder.children_folder_ids = [f.id for f in child_folders]
            
            # Find documents in this folder
            folder_documents = documents_by_folder.get(folder.id, [])
            folder.document_ids = [d.id for d in folder_documents]
            
            # Create DocumentTree nodes for children
            children = []
            
            # Add child folders (recursive)
            for child_folder in sorted(child_folders, key=lambda f: f.name):
                children.append(build_tree(child_folder))
            
            # Add documents
            for document in sorted(folder_documents, key=lambda d: d.name):
                children.append(DocumentTree(
                    data=document,
                    children=[]
                ))
            
            return DocumentTree(
                data=folder,
                children=children
            )
        
        return build_tree(root_folder)
        