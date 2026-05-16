import pytest


@pytest.mark.asyncio
async def test_start_call(client, auth_headers):
    resp = await client.post("/api/calls/start", json={}, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "call_id" in data
    assert data["websocket_url"].startswith("/ws/call/")
    return data["call_id"]


@pytest.mark.asyncio
async def test_call_history_requires_auth(client):
    resp = await client.get("/api/calls/history")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_call_history(client, auth_headers):
    resp = await client.get("/api/calls/history", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_end_call(client, auth_headers):
    start = await client.post("/api/calls/start", json={}, headers=auth_headers)
    call_id = start.json()["call_id"]
    resp = await client.post("/api/calls/end", json={"call_id": call_id}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["call_id"] == call_id


@pytest.mark.asyncio
async def test_get_call_detail(client, auth_headers):
    start = await client.post("/api/calls/start", json={}, headers=auth_headers)
    call_id = start.json()["call_id"]
    await client.post("/api/calls/end", json={"call_id": call_id}, headers=auth_headers)
    resp = await client.get(f"/api/calls/{call_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == call_id
