from collections.abc import AsyncGenerator

import pytest_asyncio
from database import close_db, get_db, init_test_db
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.sql import get_db as get_sql_db
from app.main import app
from app.models.user import User, UserRole
from app.repositories.course import CourseRepository
from app.repositories.department import DepartmentRepository
from app.repositories.major import MajorRepository
from app.repositories.user import UserRepository
from app.services.auth_service import get_password_hash


@pytest_asyncio.fixture(scope="session")
async def database() -> AsyncGenerator[AsyncSession, None]:
    await init_test_db()
    try:
        async for db in get_db():
            yield db
    finally:
        await close_db()  # type:ignore


@pytest_asyncio.fixture
async def async_client(database: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield database

    app.dependency_overrides[get_sql_db] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_repo(database: AsyncSession) -> UserRepository:
    repo = UserRepository(database)
    return repo


@pytest_asyncio.fixture
async def course_repo(database: AsyncSession) -> CourseRepository:
    course = CourseRepository(database)
    return course


@pytest_asyncio.fixture
async def department_repo(database: AsyncSession) -> DepartmentRepository:
    repo = DepartmentRepository(database)
    return repo


@pytest_asyncio.fixture
async def major_repo(database: AsyncSession) -> MajorRepository:
    repo = MajorRepository(database)
    return repo


@pytest_asyncio.fixture
async def test_user(user_repo: UserRepository) -> User:
    hashed_password = get_password_hash("123456")
    user = await user_repo.create_user(
        name="test_user", password=hashed_password, role=UserRole.student, session=0
    )
    assert user
    return user


@pytest_asyncio.fixture
async def test_admin(user_repo: UserRepository) -> User:
    hashed_password = get_password_hash("123456")
    admin = await user_repo.create_user(
        name="test_admin",
        password=hashed_password,
        role=UserRole.admin,
        session=0,
    )
    assert admin
    return admin


@pytest_asyncio.fixture
async def test_student(user_repo: UserRepository) -> User:
    hashed_password = get_password_hash("123456")
    user = await user_repo.create_user(
        name="test_student",
        password=hashed_password,
        role=UserRole.student,
        session=25,
        dept_no="DP001",
        major_no="MA001",
        class_number=2,
    )
    assert user
    return user


@pytest_asyncio.fixture
async def test_teacher(user_repo: UserRepository) -> User:
    hashed_password = get_password_hash("123456")
    user = await user_repo.create_user(
        name="test_teacher",
        password=hashed_password,
        role=UserRole.teacher,
        session=24,
        dept_no="DP001",
    )
    assert user
    return user


@pytest_asyncio.fixture
async def admin_client(async_client: AsyncClient, test_admin: User) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_admin.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client


@pytest_asyncio.fixture
async def student_client(async_client: AsyncClient, test_student: User) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_student.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client


@pytest_asyncio.fixture
async def teacher_client(async_client: AsyncClient, test_teacher: User) -> AsyncClient:
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_teacher.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    return async_client
