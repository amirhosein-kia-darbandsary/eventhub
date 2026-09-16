from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.services.feature_flag_service import set_flag
from app.api.deps import require_role
from fastapi import Depends
from app.models.webhook import FeatureFlag
from sqlalchemy import select
from app.db.session import get_db
from app.exceptions.common import NotFoundError


feature_router = APIRouter(prefix="/admin/feature-flags", tags=['features'])


class FlagUpdateRequest(BaseModel):
    enabled: bool
    rollout_percentage: int


@feature_router.put("/{flag_key}")
async def update_flag(
    flag_key: str,
    payload: FlagUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role("admin")),
):
    stmt = select(FeatureFlag).where(FeatureFlag.key == flag_key)

    result = await db.execute(stmt)
    flag = result.scalar_one_or_none()

    if not flag:
        raise NotFoundError("Feature Flag", flag_key)

    flag.enabled = payload.enabled
    flag.rollout_metadata = {
        "rollout_percentage": payload.rollout_percentage
    }

    try:    
        await set_flag(
            flag_key,
            payload.enabled,
            payload.rollout_percentage,
        )

        await db.commit()
    except Exception:
        await db.rollback()
        raise Inter
    
    
    return {
        "flag_key": flag_key,
        "enabled": payload.enabled,
        "rollout_percentage": payload.rollout_percentage,
    }