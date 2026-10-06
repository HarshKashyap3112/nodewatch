import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_alert_rules_crud(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"email": "a1@example.com", "password": "pass12345"})
    token = (await client.post("/api/v1/auth/login", json={"email": "a1@example.com", "password": "pass12345"})).json()["access_token"]
    user_headers = {"Authorization": f"Bearer {token}"}

    # Create alert rule
    rule_payload = {
        "name": "High CPU Alert",
        "metric_name": "cpu_usage_percent",
        "operator": ">",
        "threshold": 80.0,
        "is_enabled": True
    }
    create_resp = await client.post("/api/v1/alerts/rules", json=rule_payload, headers=user_headers)
    assert create_resp.status_code == 201
    rule_data = create_resp.json()
    assert rule_data["name"] == "High CPU Alert"
    assert rule_data["threshold"] == 80.0

    # List rules
    list_resp = await client.get("/api/v1/alerts/rules", headers=user_headers)
    assert list_resp.status_code == 200
    rules = list_resp.json()
    assert len(rules) == 1
