import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register user
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "password123", "full_name": "Server Owner"}
    )
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    assert data["email"] == "owner@example.com"
    assert "id" in data

    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.com", "password": "password123"}
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data

    # Login via Form Data (Swagger UI format)
    form_login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "owner@example.com", "password": "password123"}
    )
    assert form_login_resp.status_code == 200
    assert "access_token" in form_login_resp.json()

    # Get Me
    token = token_data["access_token"]
    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "owner@example.com"


@pytest.mark.asyncio
async def test_reset_password_with_secret_key(client: AsyncClient):
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "resetuser@example.com", "password": "oldpassword123", "full_name": "Reset Test User"}
    )

    # Attempt reset with invalid secret key
    invalid_resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"email": "resetuser@example.com", "reset_secret_key": "wrong_key", "new_password": "newpassword123"}
    )
    assert invalid_resp.status_code == 401

    # Reset password with valid secret key
    valid_resp = await client.post(
        "/api/v1/auth/reset-password",
        json={"email": "resetuser@example.com", "reset_secret_key": "nodewatch-reset-secret-key", "new_password": "newpassword123"}
    )
    assert valid_resp.status_code == 200

    # Login with new password
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "resetuser@example.com", "password": "newpassword123"}
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


