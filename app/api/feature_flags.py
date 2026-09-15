from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.services.feature_flag_service import set_flag
from app.api.deps import require_role
from fastapi import Depends

feature_router = APIRouter(prefix="/admin/feature-flags", tags=['features'])


class FlagUpdateRequest(BaseModel):
    enabled: bool
    rollout_percentage: int


@feature_router.put("/{flag_key}")
async def update_flag(
    flag_key: str,
    payload: FlagUpdateRequest,
    _admin=Depends(require_role("admin")),
):
    await set_flag(flag_key, payload.enabled, payload.rollout_percentage)
    return {"flag_key": flag_key, "enabled": payload.enabled, "rollout_percentage": payload.rollout_percentage}
