web: gunicorn app:app --bind 0.0.0.0:$PORT
worker: python -m examples.daily_update_scheduler
