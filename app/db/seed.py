from app.db.session import async_session_factory
from app.models.venue import Venue
from app.models.event import Event,EventStatus
from datetime import datetime, timezone, timedelta
import asyncio

async def seed():

    async with async_session_factory() as session:
        venue = Venue(name="Tehran Grand Hall",
                      address="Valiasr St", city="Tehran", capacity=500)
        session.add(venue)
        await session.flush()
        print("8"*100)
        print(venue.id)
        event = Event(
            venue_id=venue.id,
            title="EventHub Launch Night",
            starts_at=datetime.now(timezone.utc) + timedelta(days=7),
            ends_at=datetime.now(timezone.utc) + timedelta(days=7, hours=3),
            status=EventStatus.published,
        )
        session.add(event)
        await session.flush()
        
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())