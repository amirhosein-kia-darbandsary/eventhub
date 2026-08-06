import pytest

from app.exceptions.common import NotFoundError
from app.models.venue import Venue
from app.services.event_service import validate_venue_exists


class FakeVenueRepository:


    def __init__(self, venues: dict[int, Venue]):
        self._venues = venues

    async def get_by_id(self, venue_id: int) -> Venue | None:
        return self._venues.get(venue_id)


@pytest.mark.unit
async def test_validate_venue_exists_passes_when_venue_found():
    fake_venue = Venue(id=1, name="Test Hall", address="Addr", city="Tehran", capacity=100)
    repo = FakeVenueRepository({1: fake_venue})

    await validate_venue_exists(1, repo)


@pytest.mark.unit
async def test_validate_venue_exists_raises_not_found_when_missing():
    repo = FakeVenueRepository({})  

    with pytest.raises(NotFoundError) as exc_info:
        await validate_venue_exists(99999, repo)

    assert "99999" in str(exc_info.value)