#!/bin/sh
set -eu

PORT="${PORT:-8000}"

echo "Applying database migrations..."
python -m alembic upgrade head

echo "Seeding database when empty..."
python -m app.seed.seed_data

echo "Starting application on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
