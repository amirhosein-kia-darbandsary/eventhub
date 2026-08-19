from app.models.webhook import WebHookEvent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.routing import APIRouter
from fastapi import status, Request, Depends
from app.api.deps import get_db
import json
from app.workers.payment_service_worker import process_payment_webhook


webhook_router = APIRouter(prefix='/webhooks', tags=['webhook'])


@webhook_router.post("/payment", status_code=status.HTTP_200_OK)
async def webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    event_id = body.get('event_id')
    event = WebHookEvent(provider_event_id=event_id, payload=json.dumps(body))
    db.add(event)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {"status": "already_received"}
    
    process_payment_webhook.send(str(event.id))
    return {"status": "received"}
