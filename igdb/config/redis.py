import logging
import os
from contextlib import contextmanager
from typing import Union

from redis import Redis

redis_client: Union[Redis, None] = None


@contextmanager
def get_redis_connection() -> Redis:
    # This should point to the Redis container hostname in production.
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:9012")
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(redis_url)

    try:
        redis_client.ping()
        yield redis_client
    except Exception as e:
        print("Redis connection failed")
        print(e)

    finally:
        redis_client.close()
        redis_client = None
