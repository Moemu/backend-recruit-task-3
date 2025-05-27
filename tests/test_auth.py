from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
access_token: str = ""


async def test_login(async_client, test_user):
    response = await async_client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": test_user.password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print(response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()
    global access_token
    access_token = response.json()["access_token"]


async def test_logout(async_client):
    async_client.headers.update({"Authorization": f"Bearer {access_token}"})
    response = await async_client.post("/api/auth/logout")
    assert response.status_code == 200
    response = await async_client.post("/api/student/info")
    assert response.status_code != 200
