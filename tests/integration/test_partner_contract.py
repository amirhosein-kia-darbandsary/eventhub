import pytest

# If a field or fields has changed, The test is going to fail the things we need...
EXPECTED_PARTNER_EVENT_FIELDS = {
    "id", "venue_id", "title", "starts_at", "ends_at", "status"}


@pytest.mark.integration
async def test_partner_events_response_shape_is_stable(client, partner_headers, admin_client):
    venue_resp = await admin_client.post(
        "/venue", json={"name": "Contract Test Hall", "address": "Addr", "city": "Tehran", "capacity": 100}
    )
    print(venue_resp.json())
    venue_id = venue_resp.json()["id"]

    event_resp = await admin_client.post(
        "/events",
        json={
            "venue_id": venue_id, "title": "Contract Test Event",
            "starts_at": "2026-09-01T19:00:00Z", "ends_at": "2026-09-01T22:00:00Z",
        },
    )
    event_id = event_resp.json()["id"]
    await admin_client.patch(f"/events/{event_id}", json={"status": "published"})

    response = await client.get("/api/v1/partners/events", headers=partner_headers)
    assert response.status_code == 200

    body = response.json()
    assert len(body["items"]) >= 1

    actual_fields = set(body["items"][0].keys())
    missing = EXPECTED_PARTNER_EVENT_FIELDS - actual_fields
    extra = actual_fields - EXPECTED_PARTNER_EVENT_FIELDS

    assert not missing, f"Partner API contract broken -- missing fields: {missing}"
    assert not extra, f"Partner API contract broken -- unexpected new fields: {extra}"
