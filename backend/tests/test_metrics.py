import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_metrics_ingest_and_query(client: AsyncClient):
    # Setup server & agent API key
    await client.post("/api/v1/auth/register", json={"email": "m1@example.com", "password": "pass12345"})
    token = (await client.post("/api/v1/auth/login", json={"email": "m1@example.com", "password": "pass12345"})).json()["access_token"]
    user_headers = {"Authorization": f"Bearer {token}"}

    srv_resp = await client.post("/api/v1/servers", json={"name": "web-01"}, headers=user_headers)
    srv_data = srv_resp.json()
    server_id = srv_data["server"]["id"]
    api_key = srv_data["api_key"]["raw_api_key"]

    # Ingest metric push from agent
    agent_headers = {"X-Agent-API-Key": api_key}
    push_payload = {
        "hostname": "web-01.local",
        "ip_address": "192.168.1.50",
        "os_info": "Linux Ubuntu 22.04",
        "metrics": [
            {"name": "cpu_usage_percent", "value": 45.5},
            {"name": "memory_usage_percent", "value": 68.2}
        ]
    }
    ingest_resp = await client.post("/api/v1/metrics/ingest", json=push_payload, headers=agent_headers)
    assert ingest_resp.status_code == 202
    assert ingest_resp.json()["metrics_ingested"] == 2

    # Query metrics from user dashboard endpoint
    query_resp = await client.get(
        f"/api/v1/metrics/query?server_id={server_id}&metric_name=cpu_usage_percent&range=1h",
        headers=user_headers
    )
    assert query_resp.status_code == 200
    series = query_resp.json()
    assert series["metric_name"] == "cpu_usage_percent"
    assert len(series["data_points"]) == 1
    assert series["data_points"][0]["value"] == 45.5


@pytest.mark.asyncio
async def test_metrics_retention_cleanup(db_session):
    from datetime import timedelta
    from src.metrics.models import Metric
    from src.metrics.service import MetricService
    from src.models import utc_now

    now = utc_now()
    old_metric = Metric(
        server_id="srv-123",
        metric_name="cpu_usage_percent",
        timestamp=now - timedelta(days=40),
        value=50.0
    )
    new_metric = Metric(
        server_id="srv-123",
        metric_name="cpu_usage_percent",
        timestamp=now - timedelta(days=5),
        value=60.0
    )
    db_session.add_all([old_metric, new_metric])
    await db_session.commit()

    deleted_count = await MetricService.delete_old_metrics(db_session, retention_days=30)
    assert deleted_count == 1

    series = await MetricService.query_metrics(
        db=db_session,
        server_id="srv-123",
        metric_name="cpu_usage_percent",
        start_time=now - timedelta(days=60),
        end_time=now
    )
    assert len(series.data_points) == 1
    assert series.data_points[0].value == 60.0

