from typing import Any
from core.infrastructure.database.database_client import DatabaseClient
from core.models.data_room import DataRoom, DataRoomIn
from core.models.entity_status import EntityStatus

class DataRoomRepository:
    def __init__(self, database_client: DatabaseClient):
        self.db = database_client

    async def create_data_room_with_root_folder_async(self, data_room: DataRoomIn) -> DataRoom:
        commands: list[tuple[str, dict[str, Any] | None]] = [
            # Defer the foreign key constraint
            ('SET CONSTRAINTS fk_data_room_root_folder DEFERRED', None),
            
            # Create data room
            ('''
                INSERT INTO data_rooms (name, source)
                VALUES (:name, :source)
                RETURNING id, created_at, updated_at
            ''', {"name": data_room.name, "source": data_room.source.value}),

            # Create root folder
            ('''
                INSERT INTO folders (name, data_room_id, parent_folder_id)
                SELECT 'Root', d.id, NULL 
                FROM data_rooms d 
                WHERE d.name = :name AND d.source = :source
                ORDER BY d.created_at DESC 
                LIMIT 1
                RETURNING id
            ''', {"name": data_room.name, "source": data_room.source.value}),

            # Set root folder ID in data room
            ('''
                UPDATE data_rooms 
                SET root_folder_id = f.id
                FROM folders f
                WHERE data_rooms.name = :name 
                AND data_rooms.source = :source
                AND f.name = 'Root'
                AND f.data_room_id = data_rooms.id
                AND f.parent_folder_id IS NULL
                RETURNING data_rooms.id, data_rooms.created_at, data_rooms.updated_at, data_rooms.root_folder_id
            ''', {"name": data_room.name, "source": data_room.source.value})
        ]

        results = await self.db.execute_transaction_async(commands)
        result = results[3][0]

        return DataRoom(
            id=str(result["id"]),
            name=data_room.name,
            source=data_room.source,
            status=EntityStatus.ACTIVE,
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            root_folder_id=str(result["root_folder_id"]),
        )

    async def get_data_room_by_id_async(self, id: str) -> DataRoom | None:
        sql = "SELECT * FROM data_rooms WHERE id = :id"
        result = (await self.db.execute_sql_async(sql, {"id": id}))
    
        if not result:
            return None

        data_room = result[0]
        if not data_room:
            return None
        
        return DataRoom(
            id=str(data_room["id"]),
            name=data_room["name"],
            source=data_room["source"],
            created_at=data_room["created_at"],
            updated_at=data_room["updated_at"],
            status=data_room["status"],
            root_folder_id=str(data_room["root_folder_id"]),
        )