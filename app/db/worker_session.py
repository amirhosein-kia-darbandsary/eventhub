from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import get_settings
from sqlalchemy.pool import NullPool



_settings = get_settings()


worker_engine = create_async_engine(_settings.postgres.url, poolclass=NullPool)

worker_async_session_factory = async_sessionmaker(worker_engine, expire_on_commit=False)

