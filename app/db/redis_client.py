# app/db/redis_client.py
import redis.asyncio as redis
from app.core.config import settings


class RedisCache:
    client: redis.Redis = None


redis_cache = RedisCache()


async def connect_to_redis():
    print("Conectando ao Redis...")
    redis_cache.client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )
    # Testa a conexão
    await redis_cache.client.ping()
    print("Redis conectado!")


async def close_redis_connection():
    if redis_cache.client is not None:
        await redis_cache.client.close()
        print("Redis desconectado.")
