import os

from celery import Celery
from django.conf import settings


class CeleryConfigurations:
    timezone = settings.TIME_ZONE
    # SET WITH DEBUG TO NOT REPORT GRANULARITY IN PRODUCTION
    task_track_started = settings.DEBUG
    task_time_limit = 60  # seconds
    result_backend = settings.DB_CONNECTION_URI


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "metime.settings")

celery_app = Celery("metime")
celery_app.config_from_object(CeleryConfigurations)
celery_app.autodiscover_tasks()
