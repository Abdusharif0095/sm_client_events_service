import redis.asyncio as redis

from src.models import models
from lib.config import settings


redis_client: redis.Redis | None = None


async def get_redis_connection() -> redis.Redis:
    global redis_client
    if redis_client is None:
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


async def get_ping_data_from_redis(ping_uuid: str) -> models.PingData | None:
    redis_client = await get_redis_connection()

    ping_key = generate_ping_key(ping_uuid)

    ping_data = await redis_client.hgetall(ping_key)

    if not ping_data:
        return None
    
    return models.PingData(**ping_data)
