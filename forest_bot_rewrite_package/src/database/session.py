from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os
import logging
from dotenv import load_dotenv
from src.database.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to local SQLite if no DATABASE_URL is provided
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./forest_bot.db"
    logging.info(f"Using local database: {DATABASE_URL}")
else:
    logging.info("Using provided DATABASE_URL for connection.")

# Ensure the URL is async-compatible for SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
