from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection, create_async_engine
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
