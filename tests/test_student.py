from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.course import CourseType
from app.models.user import User
from app.repositories.course import CourseRepository
from app.repositories.selection import Selection
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


async def test_elective_course(
    student_client: AsyncClient,
    course_repo: CourseRepository,
    test_student: User,
    test_teacher: User,
    user_repo: UserRepository,
):
    # 创建一门选修课
    await user_repo.session.refresh(test_student)
    await course_repo.create_course(
        course_name="test_elective_course",
        teacher=test_teacher.id,
        major_no=test_student.major_no,
        session=test_student.session,
        course_type=CourseType.ELECTIVE,
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

    # 获取选修课列表
    response = await student_client.post(
        "/api/student/electives", params={"term": "2024-2025-2"}
    )
    assert response.status_code == 200
    elective_courses = response.json()
    assert elective_courses
    assert elective_courses[0]["course_name"] == "test_elective_course"

    # 选中选修课
    response = await student_client.post(
        "/api/student/select",
        params={"course_no": elective_courses[0]["course_no"]},
    )
    assert response.status_code == 200

    # 查询课表是否包含选修课
    response = await student_client.post(
        "/api/student/schedule", params={"term": "2024-2025-2"}
    )
    assert response.status_code == 200
    schedule = response.json()
    assert schedule
    assert any(course["course_name"] == "test_elective_course" for course in schedule)

    # 取消选修课
    response = await student_client.post(
        "/api/student/deselect",
        params={"course_no": elective_courses[0]["course_no"]},
    )
    assert response.status_code == 200

    # 验证课程已取消选中
    selection_result = await course_repo.session.execute(
        select(Selection).where(
            Selection.student_id == test_student.id,
            Selection.course_id == elective_courses[0]["id"],
        )
    )
    selection = selection_result.scalars().first()
    assert selection is not None
    assert selection.status is False  # 确认状态已更改

    response = await student_client.post(
        "/api/student/schedule", params={"term": "2024-2025-2"}
    )
    assert response.status_code == 200
    schedule = response.json()
    for course in schedule:
        if course["course_name"] == "test_elective_course":
            assert course["current_students"] == 0

    result = any(course["course_name"] == "test_elective_course" for course in schedule)
    assert not result
