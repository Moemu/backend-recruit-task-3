from database import async_session
from httpx import AsyncClient

from app.repositories.course import CourseRepository

test_course = ""


async def test_add_course(teacher_client: AsyncClient):
    response = await teacher_client.post(
        "/api/course/add",
        json={
            "course_name": "和沐沐一起学 Python 吧",
            "session": 24,
            "major_no": "MA001",
            "course_type": 0,
            "course_date": {
                "term": "2024-2025-2",
                "start_week": 1,
                "end_week": 16,
                "is_double_week": False,
                "week_day": 5,
                "section": [3, 4, 5],
            },
            "credit": 1.0,
            "is_public": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["course_no"]
    global test_course
    test_course = response.json()["course_no"]


async def test_info(teacher_client: AsyncClient):
    response = await teacher_client.post(
        "/api/course/info", params={"course_no": test_course}
    )
    assert response.status_code == 200
    assert response.json()["course_name"] == "和沐沐一起学 Python 吧"


async def test_submit(teacher_client: AsyncClient, course_repo: CourseRepository):
    response = await teacher_client.post(
        "/api/course/submit", params={"course_no": test_course}
    )
    assert response.status_code == 200
    course = await course_repo.get_by_course_no(test_course)
    await course_repo.session.refresh(course)
    assert course is not None
    assert course.status == 1


async def test_edit(teacher_client: AsyncClient, course_repo: CourseRepository):
    response = await teacher_client.post(
        "/api/course/edit",
        json={
            "course_no": test_course,
            "course_name": "和沐沐一起学 Java 吧",
            "course_type": 1,
            "credit": 2.0,
        },
    )
    assert response.status_code == 200
    course = await course_repo.get_by_course_no(test_course)
    await course_repo.session.refresh(course)
    assert course is not None
    assert course.course_name == "和沐沐一起学 Java 吧"
    assert course.course_type == 1
    assert course.credit == 2.0


async def test_delete(teacher_client: AsyncClient):
    response = await teacher_client.delete(
        "/api/course/delete", params={"course_no": test_course}
    )
    assert response.status_code == 200
    async with async_session() as session:
        new_repo = CourseRepository(session)
        deleted_course = await new_repo.get_by_course_no(test_course)
        assert deleted_course is None
