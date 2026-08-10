
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.db.base import Base
from sqlalchemy.pool import NullPool
from app.models import event, ticket_type, user, venue, reserve
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


@pytest_asyncio.fixture
async def admin_client(db_session, client):
    from app.core.security import hash_password
    from app.models.user import User, UserRole
    from pydantic import SecretStr

    admin = User(
        email="admin-test@eventhub.dev",
        hashed_password=hash_password(SecretStr("adminpass123")),
        full_name="Admin Test User",
        role=UserRole.admin,
    )
    db_session.add(admin)
    await db_session.flush()

    login_response = await client.post(
        "/auth/login", json={"email": "admin-test@eventhub.dev", "password": "adminpass123"}
    )
    token = login_response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    yield client


test_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def concurrency_client():

    from httpx import ASGITransport, AsyncClient

    from app.db.session import get_db
    from app.main import create_app

    app = create_app()

    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    async with test_engine.connect() as conn:
        await conn.execute(text("DELETE FROM reservations"))
        await conn.execute(text("DELETE FROM ticket_types"))
        await conn.execute(text("DELETE FROM events"))
        await conn.execute(text("DELETE FROM venues"))
        await conn.execute(text("DELETE FROM users"))
        await conn.commit()

@pytest_asyncio.fixture
async def concurrency_admin_headers(concurrency_client):
    from app.core.security import hash_password
    from app.models.user import User, UserRole
    from pydantic import SecretStr
    async with test_session_factory() as session:
        admin = User(
            email="concurrency-admin@eventhub.dev",
            hashed_password=hash_password(SecretStr("adminpass123")),
            full_name="Concurrency Admin",
            role=UserRole.admin,
        )
        session.add(admin)
        await session.commit()  

    login_response = await concurrency_client.post(
        "/auth/login",
        json={"email": "concurrency-admin@eventhub.dev", "password": "adminpass123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}