import asyncio
import uuid

import httpx
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI(title="Mock Payment Provider")

# For making our project some times failed and some times up
SIMULATE_FAILURE = {"enabled": False}


class PaymentRequest(BaseModel):
    reservation_id: int
    amount_cents: int
    callback_url: str  # Web hook address in our work we set eventhub url


class PaymentResponse(BaseModel):
    payment_id: str
    status: str


@app.post("/payments", response_model=PaymentResponse)
async def create_payment(payload: PaymentRequest, background_tasks: BackgroundTasks):
    if SIMULATE_FAILURE["enabled"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Payment provider temporarily unavailable")

    payment_id = str(uuid.uuid4())


    background_tasks.add_task(send_webhook_after_delay, payload, payment_id)

    return PaymentResponse(payment_id=payment_id, status="pending")


async def send_webhook_after_delay(payload: PaymentRequest, payment_id: str):
    await asyncio.sleep(2)  

    event_payload = {
        "event_id": str(uuid.uuid4()),  
        "payment_id": payment_id,
        "reservation_id": payload.reservation_id,
        "status": "succeeded",
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post(payload.callback_url, json=event_payload, timeout=5)
        except httpx.HTTPError:
            pass  


@app.post("/admin/simulate-failure")
async def toggle_failure(enabled: bool):
    SIMULATE_FAILURE["enabled"] = enabled
    return {"simulate_failure": enabled}