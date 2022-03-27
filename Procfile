web: gunicorn app:app
worker: celery -A tasks worker -E --loglevel=INFO