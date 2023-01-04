from django.conf import settings
from django.db import connection
from redis import Redis
from redis.client import Redis
from rest_framework.response import Response
from rest_framework.views import APIView


class Healthcheck(APIView):
    throttle_scope = "healthcheck"

    def get(self, request, format=None):
        """
        Return a response, containing flags to indicate service healthcheck.
        """

        logs = []
        status_code = 200
        is_database_working = True
        is_redis_working = True

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
        except Exception as e:
            logs.append(str(e))
            is_database_working = False
            status_code = 400

        try:
            if settings.REDIS_PASSWORD:
                redis_conn = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    socket_connect_timeout=5,
                )
            else:
                redis_conn = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    socket_connect_timeout=5,
                )
            redis_conn.ping()
        except Exception as e:
            logs.append(str(e))
            is_redis_working = False
            status_code = 400

        return Response(
            data={
                "healthcheck": "Running",
                "is_database_working": is_database_working,
                "is_redis_working": is_redis_working,
            },
            status=status_code,
        )
