import pytest


@pytest.mark.asyncio
async def test_read_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "CloudDrive API"


@pytest.mark.asyncio
async def test_auth_health(client):
    response = await client.get("/auth/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
