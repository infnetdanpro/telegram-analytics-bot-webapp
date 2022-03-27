from config import config

CELERY_BROKER_URL = config.get("REDIS_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = config.get("REDIS_URL", "redis://localhost:6379")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
