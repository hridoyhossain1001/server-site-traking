web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
worker: python -m app.services.retry_service
