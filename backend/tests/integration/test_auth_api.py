import pytest


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    resp = await client.post("/api/auth/login", json={
        "email": test_user.email, "password": "testpass123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    resp = await client.post("/api/auth/login", json={
        "email": test_user.email, "password": "wrongpassword"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client):
    resp = await client.post("/api/auth/login", json={
        "email": "nobody@nowhere.com", "password": "testpass123"
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client, test_user):
    login = await client.post("/api/auth/login", json={
        "email": test_user.email, "password": "testpass123"
    })
    refresh_token = login.json()["refresh_token"]
    resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
