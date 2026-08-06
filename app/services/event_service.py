
from app.exceptions.common import NotFoundError
from app.repositories.venue_repository import VenueRepository


async def validate_venue_exists(venue_id: int, venue_repo: VenueRepository) -> None:
    venue = await venue_repo.get_by_id(venue_id)
    if venue is None:
        raise NotFoundError("Venue", venue_id)