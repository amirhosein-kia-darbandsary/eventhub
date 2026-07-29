from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine
from app.core.config import get_settings

settings = get_settings()


engine = create_async_engine(
    url=settings.postgres.url,
    pool_size=5,
    max_overflow=10,  
    echo=settings.debug,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session_factory.begin() as session:
        yield session