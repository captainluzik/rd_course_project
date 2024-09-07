#!/bin/sh
set -e

cd /app
export PYTHONPATH=$(pwd)

until alembic upgrade head; do
    echo "Waiting for database migrations to complete..."
    sleep 2
done

uvicorn app.main:app --host 0.0.0.0 --port 8000 &

until curl -sSf http://0.0.0.0:8000/api/v1/cve/ping; do
    echo "Waiting for API to become available..."
    sleep 2
done

until python app/utils/initial_load.py; do
    echo "Waiting for initial load to complete..."
    sleep 2
done

wait