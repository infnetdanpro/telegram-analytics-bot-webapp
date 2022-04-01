from config import config

broker_url = config.get("REDIS_URL", "redis://localhost:6379")
result_backend = config.get("REDIS_URL", "redis://localhost:6379")
result_serializer = "json"
