"""
===========
celery_app.py
===========

Celery configuration for asynchronous task processing.
"""

from celery import Celery
from os import environ

celery_app = Celery('mcc',
                    broker=environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                    backend=environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=7200,
    worker_max_tasks_per_child=1,      # Forces process refresh after 1 task
    worker_prefetch_multiplier=1,      # Prevents grabbing multiple 4GB files
    task_acks_late=True,
    worker_max_memory_per_child=8000000 # 8GB limit (adjust to EC2 RAM)
)
