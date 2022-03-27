web: gunicorn app:app
celeryd: celery -A lib.celery worker -E --loglevel=INFO