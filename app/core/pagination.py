from sqlalchemy import Select, and_, or_
import base64
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, or_, and_
from typing import Any


def encode_cursor(starts_at: datetime, id_: int) -> str:
    payload = {"starts_at": starts_at.isoformat(), "id": id_}
    raw = json.dumps(payload).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def decode_cursor(cursor: str) -> tuple[datetime, int]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8"))
        payload = json.loads(raw)
        return datetime.fromisoformat(payload["starts_at"]), int(payload["id"])
    except (ValueError, KeyError, TypeError) as e:
        raise ValueError("Invalid cursor") from e


async def paginate(
    db: AsyncSession,
    stmt: Select,
    *,
    sort_column,
    id_column,
    cursor: str | None,
    limit: int,
) -> tuple[list[Any], str | None, bool]:

    if cursor is not None:
        cursor_sort_value, cursor_id = decode_cursor(cursor)

        stmt = stmt.where(
            or_(
                sort_column > cursor_sort_value,
                and_(
                    sort_column == cursor_sort_value,
                    id_column > cursor_id,
                ),
            )
        )

    stmt = (
        stmt
        .order_by(
            sort_column.asc(),
            id_column.asc(),
        )
        .limit(limit + 1)
    )

    result = await db.execute(stmt)

    rows = list(result.scalars().all())

    has_more = len(rows) > limit

    page_rows = rows[:limit]

    next_cursor = None

    if has_more and page_rows:
        last = page_rows[-1]

        last_sort_value = getattr(
            last,
            sort_column.name,
        )

        last_id = getattr(
            last,
            id_column.name,
        )

        next_cursor = encode_cursor(
            last_sort_value,
            last_id,
        )

    return page_rows, next_cursor, has_more
