import hashlib
import json

FLAGS_HASH_KEY = "feature_flags"


def _get_bucket(flag_key: str, user_id: str) -> int:
    combined = f"{flag_key}:{user_id}"
    hash_value = int(hashlib.sha256(combined.encode()).hexdigest(), 16)
    return hash_value % 100


async def is_enabled(redis_client, flag_key: str, context: dict) -> bool:

    raw = await redis_client.hget(FLAGS_HASH_KEY, flag_key)
    if raw is None:
        return False

    config = json.loads(raw)
    if not config.get("enabled", False):
        return False

    rollout_percentage = config.get("rollout_percentage", 100)
    if rollout_percentage >= 100:
        return True

    user_id = context.get("user_id")
    if user_id is None:
        return False

    return _get_bucket(flag_key, str(user_id)) < rollout_percentage


async def set_flag(redis_client, flag_key: str, enabled: bool = False, rollout_percentage: int = 100) -> None:
    config = {"enabled": enabled, "rollout_percentage": rollout_percentage}
    await redis_client.hset(FLAGS_HASH_KEY, flag_key, json.dumps(config))
