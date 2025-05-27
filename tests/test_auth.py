import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.user import User

client = TestClient(app)
access_token: str = ""


async def test_login(async_client, test_user: User):
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    global access_token
    access_token = response.json()["access_token"]


@pytest.mark.skip
async def test_logout(async_client: AsyncClient):
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    response = await async_client.post("/api/auth/logout")
    assert response.status_code == 200
    response = await async_client.post("/api/student/info")
    assert response.status_code != 200
