import hashlib
from app.core.config import get_settings

from pathlib import Path
import bcrypt
import datetime as dt
import uuid
import jwt

import secrets

_settings = get_settings()
_PRIVATE_KEY = Path(_settings.jwt.private_key_path).read_bytes()
_PUBLICK_KEY = Path(_settings.jwt.public_key_pasth).read_bytes()
_ACCESS_TOKEN_EXPIRE_TOKEN_MINUTES = _settings.jwt.access_token_expire_minutes
_REFRESH_TOKEN_EXPIRE_TOEKN_DAYS = _settings.jwt.refresh_token_expire_days

ALGORITHM = "RS256"


def hash_password(plain_password: str) -> str:

    password_bytes = plain_password.get_secret_value().encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError(
            "Password must be at most 72 bytes when UTF-8 encoded")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.get_secret_value().encode("utf-8"), hashed_password.encode("utf-8"))


def _create_token(subject: str, role: str, expires_delta: dt.timedelta, token_type: str) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(subject),
        "role": role,
        # determine kind of the token (access) or (refresh) token
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "iat": now,
        'exp': now + expires_delta
    }
    return jwt.encode(payload, _PRIVATE_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str, role: str) -> str:
    return _create_token(subject, role, dt.timedelta(minutes=_ACCESS_TOKEN_EXPIRE_TOKEN_MINUTES),
                         "access")


def create_refresh_token(subject: str, role: str) -> str:
    return _create_token(subject, role, dt.timedelta(days=_REFRESH_TOKEN_EXPIRE_TOEKN_DAYS),
                         "refresh")


def decode_token(token: str) -> dict:
    return jwt.decode(token, _PUBLICK_KEY, algorithms=[ALGORITHM])


def generate_api_key():
    return f"eh_{secrets.token_urlsafe(32)}"


def hash_api_key(raw_key: str):
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def verify_api_key(raw_key: str, hashed_key: str):
    return verify_password(raw_key, hashed_key)
