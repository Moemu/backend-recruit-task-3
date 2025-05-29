from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import CourseType
from app.models.user import User
from app.repositories.course import CourseRepository
from app.repositories.user import UserRepository

TEST_USERS: list[str] = []


async def test_info(student_client: AsyncClient):
    response = await student_client.post(
        "/api/student/info",
    )
    assert response.status_code == 200
    assert response.json()


async def test_edit(
    student_client: AsyncClient,
    user_repo: UserRepository,
    test_student: User,
    database: AsyncSession,
):
    response = await student_client.post(
        "/api/student/edit",
        params={
            "name": "test_user_edited",
            "session": 24,
            "class_number": 1,
        },
    )
    assert response.status_code == 200
    edited_user = await user_repo.get_by_name(test_student.username)
    await database.refresh(edited_user)
    assert edited_user is not None
    assert edited_user.name == "test_user_edited"
    assert edited_user.session == 24
    assert edited_user.class_number == 1


async def test_schedule(
    student_client: AsyncClient,
    course_repo: CourseRepository,
    test_student: User,
    test_teacher: User,
    user_repo: UserRepository,
):
    await user_repo.session.refresh(test_student)

    await course_repo.create_course(
        course_name="test_course",
        teacher=test_teacher.id,
        major_no=test_student.major_no,
        session=test_student.session,
        course_type=CourseType.CORE,
        credit=1.0,
        course_date={
            "term": "2024-2025-2",
            "start_week": 1,
            "end_week": 16,
            "is_double_week": False,
            "week_day": 1,
            "section": [1, 2],
        },
        is_public=True,
        status=4,
    )

    response = await student_client.post(
        "/api/student/schedule", params={"term": "2024-2025-2"}
    )
    assert response.status_code == 200
    schedule = response.json()
    assert schedule


async def test_change_password(student_client: AsyncClient, test_student: User):
    response = await student_client.post(
        "/api/student/password",
        params={"old_password": "123456", "new_password": "000000"},
    )
    assert response.status_code == 200
    response = await student_client.post(
        "/api/auth/login",
        data={"username": test_student.username, "password": "000000"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
