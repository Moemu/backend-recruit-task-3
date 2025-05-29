from database import async_session
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.course import CourseRepository
from app.repositories.department import DepartmentRepository
from app.repositories.major import MajorRepository
from app.repositories.user import UserRepository
from app.schemas.course import CourseType

TEST_USERS: list[str] = []


async def test_department_add(
    admin_client: AsyncClient, department_repo: DepartmentRepository
):
    response = await admin_client.post(
        "/api/admin/department/add",
        params={"dept_name": "计算机学院"},
    )
    assert response.status_code == 200
    response = await admin_client.post(
        "/api/admin/department/add",
        params={"dept_name": "Muika Department"},
    )
    assert response.status_code == 200
    repo = await department_repo.get_by_dept_no(response.json()["dept_no"])
    assert repo
    assert repo.dept_name == "Muika Department"


async def test_department_edit(
    admin_client: AsyncClient, department_repo: DepartmentRepository
):
    response = await admin_client.post(
        "/api/admin/department/edit",
        params={"dept_no": "DP002", "dept_name": "Muice Department"},
    )
    assert response.status_code == 200
    repo = await department_repo.get_by_dept_no("DP002")
    assert repo
    await department_repo.session.refresh(repo)
    assert repo.dept_name == "Muice Department"


async def test_department_info(admin_client: AsyncClient):
    response = await admin_client.post(
        "/api/admin/department/info",
        params={
            "dept_no": "DP001",
        },
    )
    assert response.status_code == 200
    info = response.json()
    assert info["dept_name"] == "计算机学院"
    assert info["dept_no"] == "DP001"


async def test_department_delete(admin_client: AsyncClient):
    response = await admin_client.delete(
        "/api/admin/department/delete",
        params={
            "dept_no": "DP002",
        },
    )
    assert response.status_code == 200
    async with async_session() as session:
        new_repo = DepartmentRepository(session)
        deleted_dept = await new_repo.get_by_dept_no("DP002")
        assert deleted_dept is None


async def test_major_add(admin_client: AsyncClient, major_repo: MajorRepository):
    response = await admin_client.post(
        "/api/admin/major/add",
        params={
            "major_name": "计算机科学与技术",
            "dept_no": "DP001",
        },
    )
    assert response.status_code == 200
    repo = await major_repo.get_by_major_no("MA001")
    assert repo
    assert repo.major_name == "计算机科学与技术"
    response = await admin_client.post(
        "/api/admin/major/add",
        params={
            "major_name": "软件工程",
            "dept_no": "DP001",
        },
    )


async def test_major_edit(admin_client: AsyncClient, major_repo: MajorRepository):
    response = await admin_client.post(
        "/api/admin/major/edit",
        params={
            "major_no": "MA001",
            "major_name": "计算机科学与技术（软件工程）",
            "dept_no": "DP001",
        },
    )
    assert response.status_code == 200
    repo = await major_repo.get_by_major_no("MA001")
    assert repo
    await major_repo.session.refresh(repo)
    assert repo.major_name == "计算机科学与技术（软件工程）"


async def test_major_info(admin_client: AsyncClient):
    response = await admin_client.post(
        "/api/admin/major/info",
        params={
            "major_no": "MA001",
        },
    )
    assert response.status_code == 200
    info = response.json()
    assert info["major_name"] == "计算机科学与技术（软件工程）"
    assert info["major_no"] == "MA001"
    assert info["dept_no"] == "DP001"


async def test_major_delete(admin_client: AsyncClient):
    response = await admin_client.delete(
        "/api/admin/major/delete",
        params={
            "major_no": "MA002",
        },
    )
    assert response.status_code == 200
    async with async_session() as session:
        new_repo = MajorRepository(session)
        deleted_major = await new_repo.get_by_major_no("MA002")
        assert deleted_major is None


async def test_course(
    admin_client: AsyncClient, course_repo: CourseRepository, test_teacher: User
):
    # 创建测试课程
    test_course = await course_repo.create_course(
        course_name="测试课程",
        teacher=test_teacher.id,
        major_no="MA001",
        session=25,
        course_type=CourseType.CORE,
        course_date={
            "term": "2024-2025-2",
            "start_week": 1,
            "end_week": 16,
            "is_double_week": False,
            "week_day": 5,
            "section": [3, 4, 5],
        },
        credit=1.0,
        is_public=True,
        status=1,
    )

    # 获取待审核课程
    response = await admin_client.post(
        "/api/admin/course/get_pending",
    )
    assert response.status_code == 200
    assert response.json()
    assert any(
        course["course_no"] == test_course.course_no for course in response.json()
    )

    # 测试课程审核
    response = await admin_client.post(
        "/api/admin/course/set_status",
        params={
            "course_no": test_course.course_no,
            "status": 4,
            "reason": "测试课程审核",
        },
    )
    assert response.status_code == 200
    async with async_session() as session:
        new_repo = CourseRepository(session)
        course = await new_repo.get_by_course_no(test_course.course_no)
        assert course is not None
        assert course.status == 4
        assert course.status_comment == "测试课程审核"


async def test_register(admin_client: AsyncClient, user_repo: UserRepository):
    response = await admin_client.post(
        "/api/admin/user/register",
        json={
            "role": "teacher",
            "session": 25,
            "dept_no": "DP001",
            "major_no": "MA001",
            "class_number": 2,
            "status": True,
            "name": "test_reg",
        },
    )
    print(response.json())
    assert response.status_code == 200
    username = response.json()["info"]["username"]
    user = await user_repo.get_by_name(username)
    assert user is not None
    TEST_USERS.append(user.username)


async def test_batch_register(admin_client, user_repo):
    response = await admin_client.post(
        "/api/admin/user/batch_register",
        json=[
            {
                "name": "test_bat1",
                "role": "student",
                "session": 25,
                "dept_no": "DP001",
                "major_no": "MA001",
                "class_number": 2,
            },
            {"name": "test_bat2", "role": "teacher", "session": 24, "dept_no": "DP001"},
            {"name": "test_bat3", "role": "admin", "session": 10},
        ],
    )
    assert response.status_code == 200
    infos = response.json()["infos"]
    for info in infos:
        assert await user_repo.get_by_name(info["username"])
        user = await user_repo.get_by_name(info["username"])
        TEST_USERS.append(user.username)


async def test_edit(admin_client, test_user, user_repo, database: AsyncSession):
    response = await admin_client.post(
        "/api/admin/user/edit",
        json={
            "username": test_user.username,
            "role": "teacher",
            "session": 25,
        },
    )
    assert response.status_code == 200
    edited_user = await user_repo.get_by_name(test_user.username)
    await database.refresh(edited_user)
    assert edited_user.role == UserRole.teacher
    assert edited_user.session == 25


async def test_info(admin_client: AsyncClient, test_user):
    response = await admin_client.post(
        "/api/admin/user/info",
        params={
            "username": test_user.username,
        },
    )
    assert response.status_code == 200
    assert response.json()


async def test_delete(admin_client, user_repo: UserRepository):
    for username in TEST_USERS:
        response = await admin_client.delete(
            "/api/admin/user/delete",
            params={
                "username": username,
            },
        )
        assert response.status_code == 200

        async with async_session() as session:
            new_repo = UserRepository(session)
            deleted_user = await new_repo.get_by_name(username)
            assert deleted_user is None
