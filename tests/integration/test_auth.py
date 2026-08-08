import pytest


@pytest.mark.integration
async def test_register_creates_a_user(client):
    response = await client.post(
        "/auth/register",
        json={"email": "admin@gmail.dev", "password": "securepass123", "full_name": "New User"},
    )

    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    
    
@pytest.mark.integration
async def test_full_auth_flow_register_login_protected_route(client):
    register_response = await client.post(
        "/auth/register",
        json={"email": "flowtest@eventhub.dev", "password": "securepass123", "full_name": "Flow Test"},
    )
    assert register_response.status_code == 201


    login_response = await client.post(
        "/auth/login",
        json={"email": "flowtest@eventhub.dev", "password": "securepass123"},
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    protected_response = await client.post(
        "/venue",
        json={"name": "Test Hall", "address": "Addr", "city": "Tehran", "capacity": 100},
        headers=headers,
    )
    assert protected_response.status_code == 403