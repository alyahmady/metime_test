import redis
from django.conf import settings


def get_redis_client() -> redis.Redis:
    return redis.from_url(settings.REDIS_CONNECTION_URI)
