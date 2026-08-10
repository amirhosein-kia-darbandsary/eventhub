import asyncio

import pytest
from datetime import datetime, timedelta, timezone


@pytest.mark.integration
async def test_concurrent_reservations_never_oversell(concurrency_client, concurrency_admin_headers):

    venue_resp = await concurrency_client.post(
        "/venue",
        json={"name": "Concurrency Hall", "address": "Addr",
              "city": "Tehran", "capacity": 100},
        headers=concurrency_admin_headers,
    )

    venue_id = venue_resp.json()["id"]

    event_resp = await concurrency_client.post(
        "/events",
        json={
            "venue_id": venue_id, "title": "Concurrency Test Event",
            "starts_at": "2026-09-01T19:00:00Z", "ends_at": "2026-09-01T22:00:00Z",
        },
        headers=concurrency_admin_headers,
    )
    event_id = event_resp.json()["id"]

    now = datetime.now(timezone.utc)
    day_after_now = now + timedelta(days=1)
    tt_resp = await concurrency_client.post(
        "/ticket-types",
        json={"event_id": event_id, 
              "price_cents": 10000,
              "total_quantity": 5,
              "sales_ends_at": day_after_now.isoformat(),
              "sales_start_at": now.isoformat()},
        headers=concurrency_admin_headers,
    )
    print(tt_resp.status_code)
    print(tt_resp.json())
    ticket_type_id = tt_resp.json()["id"]

    user_headers_list = [
        await _register_and_get_user_headers(concurrency_client, f"buyer{i}@eventhub.dev")
        for i in range(10)
    ]

    async def attempt_reservation(headers):
        return await concurrency_client.post(
            "/reservations",
            json={"ticket_type_id": ticket_type_id, "quantity": 1},
            headers=headers,
        )

    responses = await asyncio.gather(*[attempt_reservation(h) for h in user_headers_list])

    successes = [r for r in responses if r.status_code == 201]
    conflicts = [r for r in responses if r.status_code == 409]

    assert len(
        successes) == 5, f"باید دقیقاً ۵ تا موفق می‌شد، ولی {len(successes)} تا شد"
    assert len(
        conflicts) == 5, f"باید دقیقاً ۵ تا رد می‌شد، ولی {len(conflicts)} تا شد"


async def _register_and_get_user_headers(client, email):
    response = await client.post(
        "/auth/register",
        json={"email": email, "password": "securepass123", "full_name": "Buyer"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
