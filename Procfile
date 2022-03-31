web: gunicorn app:app --preload --max-requests 1200
worker: celery -A tasks worker --concurrency 1 -E --loglevel=INFO