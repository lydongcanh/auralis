from typing import Any
from core.infrastructure.database.database_client import DatabaseClient
from core.models.data_room import DataRoom, DataRoomIn
from core.models.entity_status import EntityStatus

class DataRoomRepository:
    def __init__(self, database_client: DatabaseClient):
        self.db = database_client

    async def create_data_room_with_root_folder_async(self, data_room: DataRoomIn) -> DataRoom:
        # First command: defer the constraint
        defer_constraint_sql = 'SET CONSTRAINTS fk_data_room_root_folder DEFERRED'
        
        # Second command: execute the CTE with all operations
        main_sql = '''
            WITH RECURSIVE
                data_room_insert AS (
                    INSERT INTO data_rooms (name, source)
                    VALUES (:name, :source)
                    RETURNING id, created_at, updated_at
                ),
                folder_insert AS (
                    INSERT INTO folders (name, data_room_id, parent_folder_id)
                    SELECT 'Root', id, NULL FROM data_room_insert
                    RETURNING id as folder_id, data_room_id
                ),
                data_room_update AS (
                    UPDATE data_rooms 
                    SET root_folder_id = folder_insert.folder_id
                    FROM folder_insert
                    WHERE data_rooms.id = folder_insert.data_room_id
                    RETURNING data_rooms.*
                )
            SELECT 
                id,
                created_at,
                updated_at,
                root_folder_id
            FROM data_room_update
        '''
        
        params: dict[str, Any] | None = {"name": data_room.name, "source": data_room.source.value}
        commands: list[tuple[str, dict[str, Any] | None]] = [
            (defer_constraint_sql, None),
            (main_sql, params)
        ]
        
        results = await self.db.execute_transaction_async(commands)
        result = results[1][0]  # Second command result, first row

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