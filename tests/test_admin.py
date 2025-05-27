from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.sql import async_session_maker
from app.models.user import User, UserRole
from app.repositories.user import UserRepository

TEST_USERS: list[User] = []


async def test_register(admin_client: AsyncClient, user_repo: UserRepository):
    response = await admin_client.post(
        "/api/admin/register",
        json={
            "role": "teacher",
            "session": 25,
            "faculty": 1,
            "major": 1,
            "class_number": 2,
            "status": True,
            "name": "test_reg",
        },
    )
    assert response.status_code == 200
    username = response.json()["info"]["username"]
    user = await user_repo.get_by_name(username)
    assert user is not None
    TEST_USERS.append(user)


async def test_batch_register(admin_client, user_repo):
    response = await admin_client.post(
        "/api/admin/batch_register",
        json=[
            {
                "name": "test_bat1",
                "role": "student",
                "session": 25,
                "faculty": 5,
                "major": 1,
                "class_number": 2,
            },
            {"name": "test_bat2", "role": "teacher", "session": 24, "faculty": 3},
            {"name": "test_bat3", "role": "admin", "session": 10, "faculty": 1},
        ],
    )
    print(response.json())
    assert response.status_code == 200
    infos = response.json()["infos"]
    for info in infos:
        assert await user_repo.get_by_name(info["username"])
        user = await user_repo.get_by_name(info["username"])
        TEST_USERS.append(user)


async def test_edit(admin_client, test_user, user_repo, database: AsyncSession):
    response = await admin_client.post(
        "/api/admin/edit",
        json={
            "username": test_user.username,
            "role": "teacher",
            "session": 25,
            "faculty": 3,
        },
    )
    assert response.status_code == 200
    edited_user = await user_repo.get_by_name(test_user.username)
    await database.refresh(edited_user)
    assert edited_user.role == UserRole.teacher
    assert edited_user.session == 25
    assert edited_user.faculty == 3


async def test_info(admin_client: AsyncClient, test_user):
    response = await admin_client.post(
        "/api/admin/info",
        params={
            "username": test_user.username,
        },
    )
    assert response.status_code == 200
    assert response.json()


async def test_delete(admin_client, user_repo: UserRepository):
    for user in TEST_USERS:
        response = await admin_client.delete(
            "/api/admin/delete",
            params={
                "username": user.username,
            },
        )
        assert response.status_code == 200

        async with async_session_maker() as session:
            new_repo = UserRepository(session)
            deleted_user = await new_repo.get_by_name(user.username)
            assert deleted_user is None
