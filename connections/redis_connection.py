import redis.asyncio as redis

from src.models import models
from lib.config import settings



async def get_redis_connection() -> redis.Redis:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    
    return redis_client


def generate_ping_key(ping_uuid: str) -> str:
    return f"ping|{ping_uuid}"


async def add_ping_data_to_redis(ping_data: models.PingData) -> None:
    redis_client = await get_redis_connection()
    ping_key = generate_ping_key(ping_data.ping_uuid)

    ping_data_dict = ping_data.__dict__

    await redis_client.hset(ping_key, mapping=ping_data_dict)
    await redis_client.expire(ping_key, settings.REDIS_PING_EXPIRE_SECONDS)


async def get_ping_data_from_redis(ping_uuid: str) -> models.PingData | None:
    redis_client = await get_redis_connection()

    ping_key = generate_ping_key(ping_uuid)

    ping_data = await redis_client.hgetall(ping_key)

    if not ping_data:
        return None
    
    return models.PingData(**ping_data)
