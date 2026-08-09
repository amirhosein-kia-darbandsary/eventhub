import pytest


@pytest.mark.integration
async def test_event_list_pagination_has_no_duplicates_or_gaps(admin_client):
    venue_response = await admin_client.post(
        "/venue",
        json={"name": "Pagination Test Hall", "address": "Addr", "city": "Tehran", "capacity": 1000},
    )
    venue_id = venue_response.json()["id"]

    event_ids = []
    for i in range(5):
        create_response = await admin_client.post(
            "/events",
            json={
                "venue_id": venue_id,
                "title": f"Event {i}",
                "starts_at": f"2026-09-0{i + 1}T19:00:00Z",
                "ends_at": f"2026-09-0{i + 1}T22:00:00Z",
            },
        )
        event_id = create_response.json()["id"]
        event_ids.append(event_id)
        await admin_client.patch(f"/events/{event_id}", json={"status": "published"})

    page1 = await admin_client.get("/events", params={"limit": 2})
    page1_body = page1.json()
    assert len(page1_body["items"]) == 2
    assert page1_body["has_more"] is True

    page2 = await admin_client.get("/events", params={"limit": 2, "cursor": page1_body["next_cursor"]})
    page2_body = page2.json()
    assert len(page2_body["items"]) == 2

    page1_ids = {item["id"] for item in page1_body["items"]}
    page2_ids = {item["id"] for item in page2_body["items"]}
    assert page1_ids.isdisjoint(page2_ids)