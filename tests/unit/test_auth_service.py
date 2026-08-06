from app.models.user import UserRole, User
from app.exceptions.auth_exception import ForbiddenError
from app.api.deps import require_role
import pytest
from app.core.security import *
from pydantic import SecretStr


@pytest.mark.unit
def test_hash_password_returns_deffrent_values():
    password = SecretStr("123456")
    hashed_password = hash_password(password)

    assert password.get_secret_value() != hashed_password


@pytest.mark.unit
def test_hash_password_is_not_empty():
    hashed = hash_password(SecretStr("123456"))
    assert hashed


@pytest.mark.unit
def test_hash_password_generates_unique_hashes():
    password = SecretStr("123456")

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2


@pytest.mark.unit
def test_verify_password_success():
    password = SecretStr("123456")

    hashed = hash_password(password)

    assert verify_password(password, hashed)


@pytest.mark.unit
def test_create_access_token_is_not_empty():
    token = create_access_token(
        subject="1",
        role="admin",
    )
    assert isinstance(token, str)
    assert token != ""


@pytest.mark.unit
def test_refresh_token_has_right_fields():
    token = create_refresh_token(
        subject="1",
        role="admin",
    )
    payload = decode_token(token=token)

    assert payload["sub"] == "1"
    assert payload["role"] == "admin"
    assert "exp" in payload


@pytest.mark.unit
async def test_require_role_allows_admin():
    checker = require_role("admin")

    user = User(
        role=UserRole.admin,
    )

    result = await checker(user)

    assert result is user


@pytest.mark.unit
async def test_require_role_raises_forbidden():
    checker = require_role("admin")

    user = User(
        role=UserRole.customer,
    )

    with pytest.raises(ForbiddenError) as exc:
        await checker(user)

    assert "admin" in str(exc.value)
