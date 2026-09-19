import pytest
from app.services.feature_flag_service import _get_bucket, is_enabled, set_flag
from tests.integration.conftest import fake_redis_client #


@pytest.mark.unit
async def test_flag_disabled_by_default_when_not_set(fake_redis_client):
    flag_key = "TEST_FLAG_FEATURES"
    rollout_percentage = 30
    await set_flag(fake_redis_client,flag_key, rollout_percentage=rollout_percentage)
    enabled = await is_enabled(redis_client=fake_redis_client, flag_key=flag_key, context={"user_id":10})
    assert False == enabled


@pytest.mark.unit
async def test_flag_enabled_at_100_percent_always_true(fake_redis_client):
    flag_key = "TEST_FLAG_FEATURES"
    rollout_percentage = 100
    enable = True

    await set_flag(fake_redis_client, flag_key=flag_key, enabled=enable,
             rollout_percentage=rollout_percentage)
    enabled = await is_enabled(fake_redis_client, flag_key, context={"user_id": 10})

    assert enabled == True


@pytest.mark.unit
async def test_flag_rollout_percentage_is_deterministic_per_user(fake_redis_client):
    bucket1 = _get_bucket("waitlist_enabled", "user-42")
    bucket2 = _get_bucket("waitlist_enabled", "user-42")
    assert bucket1 == bucket2
