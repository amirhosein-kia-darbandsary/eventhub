import pytest


@pytest.mark.integration
async def test_admin_can_create_and_read_venue(admin_client):
    create_response = await admin_client.post("/venue",
                                              json={
                                                  "name": "Tehran Grand Hall", "address": "Valiasr St", "city": "Tehran", "capacity": 500}
                                              )
    assert create_response.status_code == 201
    venue_id = create_response.json()["id"]
    get_response = await admin_client.get(f"/venue/{venue_id}")

    assert get_response.status_code == 200

    assert get_response.json().get("name") == "Tehran Grand Hall"


@pytest.mark.integration
async def test_create_event_with_nonexistent_venue_returns_404(admin_client):
    response = await admin_client.post(
        "/events",
        json={
            "venue_id": 999999,
            "title": "Ghost Event",
            "starts_at": "2026-09-01T19:00:00Z",
            "ends_at": "2026-09-01T22:00:00Z",
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
