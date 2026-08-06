

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.venue import Venue


class VenueRepository(Protocol):

    async def get_by_id(self, venue_id: int) -> Venue | None: ...


class SqlAlchemyVenueRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, venue_id: int) -> Venue | None:
        return await self.db.get(Venue, venue_id)
    
