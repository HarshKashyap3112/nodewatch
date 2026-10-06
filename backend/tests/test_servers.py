import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_server_management(client: AsyncClient):
    # Register owner
    reg = await client.post("/api/v1/auth/register", json={"email": "s1@example.com", "password": "pass12345"})
    assert reg.status_code == 201
    token = (await client.post("/api/v1/auth/login", json={"email": "s1@example.com", "password": "pass12345"})).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create server
    create_resp = await client.post(
        "/api/v1/servers",
        json={"name": "prod-db-01", "hostname": "db01.infra.local"},
        headers=headers
    )
    assert create_resp.status_code == 201
    server_data = create_resp.json()
    assert server_data["server"]["name"] == "prod-db-01"
    assert "raw_api_key" in server_data["api_key"]
    assert server_data["api_key"]["raw_api_key"].startswith("smp_")

    # List servers
    list_resp = await client.get("/api/v1/servers", headers=headers)
    assert list_resp.status_code == 200
    servers = list_resp.json()
    assert len(servers) == 1
    assert servers[0]["name"] == "prod-db-01"
