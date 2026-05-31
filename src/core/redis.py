from __future__ import annotations

from redis.asyncio import ConnectionPool, Redis

from src.core.config import settings

redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None


async def init_redis() -> None:
    """Initialize the Redis connection pool and client."""
    global redis_pool, redis_client
    try:
        redis_pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
        redis_client = Redis(connection_pool=redis_pool)
        await redis_client.ping()
        print("Redis connected successfully")
    except Exception:
        print("WARNING: Redis not available. Token blacklist disabled.")
        redis_client = None
        redis_pool = None


async def close_redis() -> None:
    """Close the Redis connection pool."""
    global redis_pool, redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
    if redis_pool:
        await redis_pool.disconnect()
        redis_pool = None


async def get_redis() -> Redis | None:
    """Dependency that returns the Redis client (or None if not available)."""
    return redis_client
