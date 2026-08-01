import base64
import json
from datetime import datetime


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