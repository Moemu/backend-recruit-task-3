from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.sql import close_db, load_db
from app.deps.sql import get_db
from app.main import app
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.services.auth_service import get_password_hash


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def database() -> AsyncGenerator[AsyncSession, None]:
    await load_db()
    try:
        async for db in get_db():
            yield db
    finally:
        await close_db()  # type:ignore


@pytest_asyncio.fixture
async def user_repo(database: AsyncSession) -> UserRepository:
    repo = UserRepository(database)
    return repo


@pytest_asyncio.fixture
async def test_admin(user_repo: UserRepository) -> User:
    admin = await user_repo.create_user(
        name=config.test.test_admin_username,
        password=get_password_hash(config.test.test_admin_password),
        role=UserRole.admin,
        session=0,
        faculty=0,
    )
    admin.password = config.test.test_admin_password
    return admin


@pytest_asyncio.fixture
async def test_user(user_repo: UserRepository) -> User:
    user = await user_repo.create_user(
        name="test_user",
        password="123456",
        role=UserRole.student,
        session=0,
        faculty=0,
        major=0,
        class_number=0,
    )
    user.password = config.test.test_admin_password
    return user


@pytest_asyncio.fixture
async def admin_client(async_client: AsyncClient, test_admin) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_admin.username, "password": test_admin.password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client
