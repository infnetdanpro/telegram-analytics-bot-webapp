web: gunicorn app:app
worker: celery -A tasks worker --concurrency 1 -E --loglevel=INFO