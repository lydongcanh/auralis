from typing import Any
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import text

from core.utils.env import get_required_env

class DatabaseClient:
    def __init__(self):
        database_url = get_required_env("DATABASE_URL")        
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

    async def execute_sql_async(self, sql: str, params: dict | None = None) -> list[dict]:
        async with self.engine.connect() as connection:
            result = await connection.execute(text(sql), params or {})
            await connection.commit()
            rows = result.mappings().all()
            await connection.close()
            return [dict(row) for row in rows]
    
    async def execute_transaction_async(self, commands: list[tuple[str, dict[str, Any] | None]]) -> list[list[dict]]:
        """
        Execute multiple SQL commands in a single transaction.
        
        Args:
            commands: List of tuples where each tuple contains (sql_string, params_dict)
        
        Returns:
            List of results for each command, where each result is a list of dictionaries
        """
        async with self.engine.connect() as connection:
            async with connection.begin():
                results = []
                for sql, params in commands:
                    result = await connection.execute(text(sql), params or {})
                    try:
                        # Try to get rows - some commands like SET don't return rows
                        rows = result.mappings().all()
                        results.append([dict(row) for row in rows])
                    except Exception:
                        # Command doesn't return rows (like SET CONSTRAINTS)
                        results.append([])
            await connection.close()
            return results
        
