import pytest


@pytest.mark.integration
async def test_cannot_register_users_with_same_email(client):

    payload = {"email": "duplicate@eventhub.dev",
               "password": "securepass123", "full_name": "First User"}
    first_reponse = await client.post('/auth/register', json=payload)
    assert first_reponse.status_code == 201

    
    second_response = await client.post('/auth/register', json=payload)
    assert second_response.status_code == 409 
