from app.db.session import async_session_factory
import asyncio
from sqlalchemy import text


stmt = """
EXPLAIN ANALYZE
SELECT * FROM events
WHERE status = 'published'
ORDER BY starts_at ASC, id ASC
LIMIT 20;
"""


async def test_postgres_planner():
    async with async_session_factory() as session:
        result = await session.execute(text(stmt))

        rows = result.fetchall()

        for row in rows:
            print(row[0])


if __name__ == "__main__":
    asyncio.run(test_postgres_planner())