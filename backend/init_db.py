import asyncio
from sqlalchemy import text
from backend.database import engine, Base

async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        print("pgvector extension vefied/enabled.")
        await conn.run_sync(Base.metadata.create_all)
        print("Schema created.")

if __name__ == "__main__":
    asyncio.run(init_db())
