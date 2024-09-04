#!/bin/sh
set -e

cd /app
export PYTHONPATH=$(pwd)

# Выполните миграции
until alembic upgrade head; do
    echo "Waiting for database migrations to complete..."
    sleep 2
done

# Запустите начальную загрузку
until python app/utils/initial_load.py; do
    echo "Waiting for initial load to complete..."
    sleep 2
done

# Запустите сервер
uvicorn app.main:app --host 0.0.0.0 --port 8000
