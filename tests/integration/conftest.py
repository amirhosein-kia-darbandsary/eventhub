
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.db.base import Base
from sqlalchemy.pool import NullPool
from app.models import event, ticket_type, user, venue
# Just for register in BaseModel when we want to run the tests in single state not all of
# them together when you run for example just constraint test alone you'll get an error
# about Undefined Table Error that means in the Base.metadata.create_all python can't figure
# which models are...
settings = Settings(_env_file=".env.test")

test_engine = create_async_engine(settings.postgres.url, poolclass=NullPool)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """For one test session, create the tables once and drop them at the end.
    In practice, use **Alembic migrations** instead of `metadata.create_all`; 
    the final test setup should run `alembic upgrade head` so tests run against 
    the actual migration schema.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """
    Each test runs inside its own SAVEPOINT/transaction* At the end of the test,
    the transaction is automatically rolled back, whether the test passes or fails. 
    This keeps tests isolated from each other without rebuilding the database from 
    scratch for every test.
    """

    async with test_engine.connect() as connection:
        await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )
        session = session_factory()
        yield session
        await session.close()
        await connection.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    from app.db.session import get_db
    from app.main import create_app
    from fastapi.testclient import TestClient
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as test_client:
        yield test_client
